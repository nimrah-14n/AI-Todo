import { useState } from 'react'
import ChatInterface from '../components/ChatInterface'

export default function Home() {
  // Use test user ID directly
  const TEST_USER_ID = '00000000-0000-0000-0000-000000000001';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-semibold text-gray-900">Todo AI Chatbot</h1>
        </div>
      </header>

      {/* Chat Interface */}
      <main className="h-[calc(100vh-60px)]">
        <ChatInterface userId={TEST_USER_ID} />
      </main>
    </div>
  )
}
