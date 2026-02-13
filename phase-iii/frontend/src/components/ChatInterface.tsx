/**
 * ChatInterface Component
 *
 * Main chat interface for the Todo AI Chatbot using OpenAI ChatKit.
 * Handles message sending, conversation state, and optimistic updates.
 */
'use client';

import React, { useState, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  id?: string;
  isOptimistic?: boolean;
}

interface ChatInterfaceProps {
  userId: string;
}

export default function ChatInterface({ userId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load conversation history on mount
  useEffect(() => {
    loadConversationHistory();
  }, [userId]);

  const loadConversationHistory = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      // Get list of conversations
      const response = await fetch(`${apiUrl}/api/${userId}/conversations`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });

      if (!response.ok) return;

      const data = await response.json();

      if (data.conversations && data.conversations.length > 0) {
        // Load most recent conversation
        const latestConv = data.conversations[0];
        setConversationId(latestConv.id);

        // Load messages
        const historyResponse = await fetch(`${apiUrl}/api/${userId}/conversations/${latestConv.id}`, {
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`
          }
        });

        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          setMessages(historyData.messages.map((msg: any) => ({
            role: msg.role,
            content: msg.content,
            id: Math.random().toString()
          })));
        }
      }
    } catch (err) {
      console.error('Failed to load conversation history:', err);
    }
  };

  const getAuthToken = (): string => {
    // Get auth token from localStorage or context
    const auth = localStorage.getItem('auth');
    if (auth) {
      const authData = JSON.parse(auth);
      return authData.token || '';
    }
    return '';
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const userMessage: Message = {
      role: 'user',
      content: inputValue.trim(),
      id: Math.random().toString(),
      isOptimistic: true
    };

    // Optimistic update: add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/api/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      // Remove optimistic flag from user message
      setMessages(prev => prev.map(msg =>
        msg.id === userMessage.id ? { ...msg, isOptimistic: false } : msg
      ));

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        id: Math.random().toString()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update conversation ID
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

    } catch (err) {
      console.error('Error sending message:', err);

      // Rollback optimistic update
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));

      setError('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-interface flex flex-col h-full max-w-4xl mx-auto">
      {/* Messages Container */}
      <div className="messages-container flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg">Welcome to Todo AI Chatbot!</p>
            <p className="text-sm mt-2">Ask me to create, view, complete, or manage your tasks.</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`message flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`message-bubble max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-200 text-gray-900'
              } ${message.isOptimistic ? 'opacity-70' : ''}`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message flex justify-start">
            <div className="message-bubble bg-gray-200 text-gray-900 rounded-lg px-4 py-2">
              <p className="text-sm">Typing...</p>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mx-4">
          {error}
        </div>
      )}

      {/* Input Container */}
      <div className="input-container border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 disabled:bg-gray-100"
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
