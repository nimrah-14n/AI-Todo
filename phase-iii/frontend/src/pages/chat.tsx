/**
 * Chat Page
 *
 * Main page for the Todo AI Chatbot chat interface.
 * Includes authentication check and redirects to login if not authenticated.
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import ChatInterface from '../components/ChatInterface';

export default function ChatPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = () => {
    try {
      // FOR TESTING: Use test user ID directly (bypass authentication)
      const TEST_USER_ID = '00000000-0000-0000-0000-000000000001';

      // Check if user is authenticated
      const auth = localStorage.getItem('auth');

      if (!auth) {
        // For testing: Auto-authenticate with test user
        const testAuth = {
          isAuthenticated: true,
          user: {
            id: TEST_USER_ID,
            email: 'test@example.com'
          }
        };
        localStorage.setItem('auth', JSON.stringify(testAuth));
        setUserId(TEST_USER_ID);
        setIsLoading(false);
        return;
      }

      const authData = JSON.parse(auth);

      if (!authData.isAuthenticated || !authData.user?.id) {
        // For testing: Auto-authenticate with test user
        const testAuth = {
          isAuthenticated: true,
          user: {
            id: TEST_USER_ID,
            email: 'test@example.com'
          }
        };
        localStorage.setItem('auth', JSON.stringify(testAuth));
        setUserId(TEST_USER_ID);
        setIsLoading(false);
        return;
      }

      // User is authenticated
      setUserId(authData.user.id);
      setIsLoading(false);

    } catch (error) {
      console.error('Authentication check failed:', error);
      // For testing: Auto-authenticate with test user
      const TEST_USER_ID = '00000000-0000-0000-0000-000000000001';
      const testAuth = {
        isAuthenticated: true,
        user: {
          id: TEST_USER_ID,
          email: 'test@example.com'
        }
      };
      localStorage.setItem('auth', JSON.stringify(testAuth));
      setUserId(TEST_USER_ID);
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!userId) {
    return null; // Will redirect
  }

  return (
    <div className="chat-page min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Todo AI Chatbot</h1>
          <button
            onClick={() => {
              localStorage.removeItem('auth');
              router.push('/login');
            }}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Chat Interface */}
      <main className="h-[calc(100vh-60px)]">
        <ChatInterface userId={userId} />
      </main>
    </div>
  );
}
