import React, { useEffect, useRef, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/useRedux';
import {
  setSessions,
  setActiveSession,
  setMessages,
  addMessage,
  updateLastMessage,
  setLoading,
  setStreaming,
  setError,
} from '../store/chatSlice';
import api from '../api/client';
import { API_BASE_URL, AUTH_TOKEN_KEY } from '../constants';
import { Send, Bot, User, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../utils';

function MessageSkeleton() {
  return (
    <div className="flex gap-4 max-w-4xl mx-auto w-full animate-pulse">
      <div className="w-10 h-10 rounded-xl bg-zinc-800 shrink-0" />
      <div className="flex flex-col space-y-3 flex-1">
        <div className="h-4 bg-zinc-800 rounded-md w-3/4" />
        <div className="h-4 bg-zinc-800 rounded-md w-1/2" />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const dispatch = useAppDispatch();
  const { messages, activeSessionId, loading, streaming, error } = useAppSelector((state) => state.chat);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (activeSessionId) {
      fetchMessages(activeSessionId);
    }
  }, [activeSessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, streaming]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSessions = async () => {
    try {
      const response = await api.get('/chat/sessions');
      // normalize backend snake_case to frontend camelCase
      const sessions = (response.data || []).map((s: any) => ({
        id: s.id,
        title: s.title,
        createdAt: s.created_at || s.createdAt,
        updatedAt: s.updated_at || s.updatedAt,
      }));
      dispatch(setSessions(sessions));
    } catch (err) {
      console.error('Failed to fetch sessions', err);
    }
  };

  const fetchMessages = async (sessionId: string) => {
    dispatch(setLoading(true));
    try {
      const response = await api.get(`/chat/${sessionId}`);
      // normalize messages: backend uses created_at and may not include id
      const data = response.data;
      const msgs = (data.messages || []).map((m: any, idx: number) => ({
        id: m.id || `${Date.now()}-${idx}`,
        role: m.role,
        content: m.content,
        timestamp: m.created_at || m.timestamp || new Date().toISOString(),
      }));
      dispatch(setMessages(msgs));
    } catch (err) {
      dispatch(setError('Failed to load messages'));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;

    const userMessage: any = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    dispatch(addMessage(userMessage));
    setInput('');
    dispatch(setStreaming(true));
    dispatch(setError(null));

    let sessionId = activeSessionId;

    try {
      // If no active session, create one first
      if (!sessionId) {
        const sessionResponse = await api.post('/chat/session', { title: input.substring(0, 30) });
        sessionId = sessionResponse.data.id;
        dispatch(setActiveSession(sessionId));
        fetchSessions();
      }

      // Prepare assistant placeholder
      const assistantMessageId = (Date.now() + 1).toString();
      dispatch(addMessage({
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      }));

      // Streaming logic
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          content: input,
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No readable stream');

      const decoder = new TextDecoder();
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // Assuming the backend sends raw text or SSE.
        // If SSE, you'd parse "data: ..."
        accumulatedContent += chunk;
        dispatch(updateLastMessage(accumulatedContent));
      }
    } catch (err: any) {
      dispatch(setError('Something went wrong. Please try again.'));
      console.error(err);
    } finally {
      dispatch(setStreaming(false));
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 lg:p-8 space-y-8 custom-scrollbar"
      >
        <AnimatePresence mode="popLayout">
          {loading && messages.length === 0 && (
            <motion.div
              key="skeletons"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              <MessageSkeleton />
              <MessageSkeleton />
              <MessageSkeleton />
            </motion.div>
          )}

          {messages.length === 0 && !loading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto"
            >
              <div className="w-20 h-20 rounded-3xl bg-indigo-600/10 flex items-center justify-center mb-6">
                <Sparkles className="w-10 h-10 text-indigo-500" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-3">How can I help you today?</h2>
              <p className="text-zinc-400 text-lg leading-relaxed">
                Nexus AI is your production-grade assistant. Ask me anything from complex coding problems to creative writing.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-12 w-full">
                {['Explain quantum computing', 'Write a Python script', 'Design a SaaS landing page', 'Help me with my resume'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="p-4 text-left text-sm bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 hover:border-indigo-500/30 transition-all"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "flex gap-4 max-w-4xl mx-auto",
                message.role === 'user' ? "flex-row-reverse" : "flex-row"
              )}
            >
              <div className={cn(
                "w-10 h-10 rounded-xl shrink-0 flex items-center justify-center",
                message.role === 'user'
                  ? "bg-indigo-600"
                  : "bg-zinc-800 border border-white/10"
              )}>
                {message.role === 'user' ? <User className="w-6 h-6 text-white" /> : <Bot className="w-6 h-6 text-indigo-400" />}
              </div>
              <div className={cn(
                "flex flex-col space-y-2 max-w-[85%]",
                message.role === 'user' ? "items-end" : "items-start"
              )}>
                <div className={cn(
                  "px-5 py-3 rounded-2xl text-sm leading-relaxed",
                  message.role === 'user'
                    ? "bg-indigo-600 text-white rounded-tr-none"
                    : "bg-[#1A1A1A] text-zinc-200 border border-white/5 rounded-tl-none"
                )}>
                  {message.role === 'assistant' && message.content === '' && streaming ? (
                    <div className="flex flex-col space-y-2 w-64 animate-pulse">
                      <div className="h-3 bg-zinc-700 rounded w-full" />
                      <div className="h-3 bg-zinc-700 rounded w-5/6" />
                      <div className="h-3 bg-zinc-700 rounded w-4/6" />
                    </div>
                  ) : (
                    <div className="markdown-body">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {error && (
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <AlertCircle className="w-5 h-5" />
              {error}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 lg:p-8 pt-0">
        <div className="max-w-4xl mx-auto relative">
          <form
            onSubmit={handleSendMessage}
            className="relative flex items-center"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message Nexus AI..."
              disabled={streaming}
              className="w-full bg-[#1A1A1A] border border-white/10 rounded-2xl py-4 pl-6 pr-16 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all disabled:opacity-50 shadow-2xl"
            />
            <button
              type="submit"
              disabled={!input.trim() || streaming}
              className="absolute right-3 p-2.5 rounded-xl bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 disabled:bg-zinc-800 transition-all"
            >
              {streaming ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
          <p className="mt-3 text-center text-[10px] text-zinc-600 uppercase tracking-widest font-medium">
            Nexus AI can make mistakes. Check important info.
          </p>
        </div>
      </div>
    </div>
  );
}
