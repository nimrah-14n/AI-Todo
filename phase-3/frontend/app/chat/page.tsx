'use client'

import ChatInterface from '../../components/ChatInterface'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ChatPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/signin')
    }
  }, [status, router])

  if (status === 'loading') {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!session?.user?.id) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ChatInterface userId={session.user.id} />
    </div>
  )
}
