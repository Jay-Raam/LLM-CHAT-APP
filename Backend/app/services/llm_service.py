import asyncio
import json
import logging
import random
from typing import AsyncGenerator, List

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.url = str(settings.OPENROUTER_URL)
        self.api_key = settings.OPENROUTER_API_KEY
        self.use_mock = bool(getattr(settings, "USE_MOCK_LLM", False))

    async def stream_chat(self, messages: List[dict]) -> AsyncGenerator[str, None]: # type: ignore
        """
        Stream chat completion from OpenRouter (gpt-oss-20b:free).
        This method parses line-delimited / SSE-style JSON responses and yields
        plain text deltas (not raw SSE). It honors 429 Retry-After when present
        and uses exponential backoff with jitter.
        """
        # If configured to use the mock LLM (dev), yield a canned streaming
        # response and return immediately.
        if self.use_mock or not self.api_key:
            # simple mock: split a canned reply into words and stream them
            mock_reply = "This is a mock response from Nexus AI. The external LLM is disabled or unreachable."
            for word in mock_reply.split():
                yield word + " "
                await asyncio.sleep(0.02)
            return

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": "gpt-oss-20b:free", "messages": messages, "stream": True} # type: ignore

        max_retries = 5
        attempt = 0

        while True:
            try:
                timeout = httpx.Timeout(60.0, read=120.0)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", self.url, json=payload, headers=headers) as resp: # pyright: ignore[reportUnknownArgumentType]
                        # handle immediate non-stream errors
                        if resp.status_code == 429:
                            # May include Retry-After header
                            retry_after = resp.headers.get("Retry-After")
                            raise httpx.HTTPStatusError("rate_limited", request=resp.request, response=resp)
                        resp.raise_for_status()

                        buffer = ""
                        async for raw_chunk in resp.aiter_text(chunk_size=1024):
                            if not raw_chunk:
                                continue
                            buffer += raw_chunk
                            # SSE events are separated by double newlines
                            while "\n\n" in buffer:
                                event, buffer = buffer.split("\n\n", 1)
                                event = event.strip()
                                if not event:
                                    continue
                                # lines may start with 'data: '
                                if event.startswith("data:"):
                                    # remove all leading 'data: ' prefixes (support multi-line data)
                                    lines = [ln[len("data:"):].strip() if ln.startswith("data:") else ln for ln in event.splitlines()]
                                    data_str = "\n".join(lines).strip()
                                else:
                                    data_str = event

                                # Some SSE streams send a literal [DONE]
                                if data_str == "[DONE]":
                                    return

                                # Try to parse JSON; if fails, yield raw text
                                try:
                                    payload_json = json.loads(data_str)
                                except Exception:
                                    # yield raw text chunk
                                    yield data_str
                                    continue

                                # Extract text delta from known structures
                                # OpenRouter / OpenAI-like: {choices: [{delta: {content: '...'}}]}
                                text_piece = ""
                                choices = payload_json.get("choices") or [] # type: ignore
                                for c in choices: # pyright: ignore[reportUnknownVariableType]
                                    # delta.content
                                    delta = c.get("delta") or {} # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                                    if isinstance(delta, dict) and "content" in delta:
                                        text_piece += delta.get("content") or "" # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
                                    # full message
                                    message = c.get("message") or {} # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                                    if isinstance(message, dict):
                                        text_piece += message.get("content") or "" # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
                                    # older format: text directly
                                    if "text" in c:
                                        text_piece += c.get("text") or "" # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

                                if text_piece:
                                    yield text_piece
                        # finish any remaining buffer (non-SSE provider may stream raw JSON)
                        if buffer.strip():
                            try:
                                # try parse last JSON
                                last = json.loads(buffer)
                                # best-effort: extract content field
                                if isinstance(last, dict):
                                    # pull choices if present
                                    choices = last.get("choices") or [] # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                                    text_piece = ""
                                    for c in choices: # pyright: ignore[reportUnknownVariableType]
                                        delta = c.get("delta") or {} # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                                        if isinstance(delta, dict) and "content" in delta:
                                            text_piece += delta.get("content") or "" # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
                                        message = c.get("message") or {} # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                                        if isinstance(message, dict):
                                            text_piece += message.get("content") or "" # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
                                    if text_piece:
                                        yield text_piece
                            except Exception:
                                yield buffer
                # if we reached here without exceptions, break loop
                break
            except httpx.HTTPStatusError as e:
                attempt += 1
                resp = getattr(e, "response", None)
                status = resp.status_code if resp is not None else None
                if status == 429 and attempt <= max_retries:
                    retry_after = None
                    try:
                        retry_after = int(resp.headers.get("Retry-After")) if resp and resp.headers.get("Retry-After") else None
                    except Exception:
                        retry_after = None
                    backoff = (2 ** attempt) + random.random()
                    wait = retry_after if retry_after is not None else min(backoff, 30)
                    logger.warning("Rate limited by LLM provider (429). retrying in %s seconds (attempt %s)", wait, attempt)
                    await asyncio.sleep(wait)
                    continue
                logger.exception("LLM provider HTTP error: %s", str(e))
                yield f"[ERROR] LLM provider HTTP error: {str(e)}"
                break
            except (httpx.ConnectError, httpx.TransportError) as e:
                # Detect DNS resolution failures (getaddrinfo) and immediately
                # provide the mock fallback instead of repeatedly retrying.
                err_text = str(e).lower()
                if "getaddrinfo failed" in err_text or "name or service not known" in err_text or "temporary failure in name resolution" in err_text:
                    logger.error("LLM DNS resolution failed: %s", err_text)
                    fallback = "[ERROR] LLM provider unreachable (DNS) — using local fallback."
                    for w in fallback.split():
                        yield w + " "
                        await asyncio.sleep(0.02)
                    break

                attempt += 1
                logger.warning("LLM connection error (attempt %s): %s", attempt, str(e))
                if attempt <= max_retries:
                    backoff = min(2 ** attempt + random.random(), 30)
                    await asyncio.sleep(backoff)
                    continue
                logger.exception("LLM provider connect error final: %s", str(e))
                # provide a fallback mock reply so the UI still gets content
                fallback = "[ERROR] LLM provider unreachable — using local fallback."
                for w in fallback.split():
                    yield w + " "
                    await asyncio.sleep(0.02)
                break
            except Exception as e:
                attempt += 1
                if attempt <= max_retries:
                    backoff = min(2 ** attempt + random.random(), 30)
                    logger.warning("LLM stream failed, retrying in %s seconds (attempt %s): %s", backoff, attempt, str(e))
                    await asyncio.sleep(backoff)
                    continue
                logger.exception("Unexpected LLM error: %s", str(e))
                yield f"[ERROR] Unexpected LLM error: {str(e)}"
                break
