'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import Header from '../components/Header'
import ReactMarkdown from 'react-markdown'
import Link from 'next/link'

export default function ProChat() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [credits, setCredits] = useState(0)
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  const [isAsking, setIsAsking] = useState(false)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/auth/signin')
      return
    }
    setUser(user)
    await loadCredits(user.id)
    setLoading(false)
  }

  const loadCredits = async (userId: string) => {
    const { data } = await supabase
      .from('user_credits')
      .select('balance')
      .eq('user_id', userId)
      .single()
    
    setCredits(data?.balance || 0)
  }

  const handleAsk = async () => {
    if (!query.trim() || isAsking) return

    // Check credits
    if (credits < 10) {
      alert('Insufficient credits! You need 10 credits per query.')
      router.push('/get-credits')
      return
    }

    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setIsAsking(true)

    try {
      const response = await fetch('/api/pro-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          userId: user.id 
        })
      })

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }

      const aiMessage = { 
        role: 'assistant', 
        content: data.response,
        models: data.models 
      }
      setMessages(prev => [...prev, aiMessage])
      
      // Reload credits after successful query
      await loadCredits(user.id)
    } catch (error: any) {
      const errorMessage = { 
        role: 'assistant', 
        content: `Error: ${error.message}`,
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsAsking(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white flex items-center justify-center">
        <div className="text-2xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      <Header />

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Title & Credits */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-black mb-4 bg-gradient-to-r from-orange-400 via-yellow-400 to-orange-500 bg-clip-text text-transparent">
            NFL Pro Chat ⚡
          </h1>
          <p className="text-slate-400 text-lg mb-4">
            Ask anything about this week's NFL games. Powered by AI + Live Data.
          </p>
          
          {/* Credit Balance */}
          <div className="inline-flex items-center gap-4 bg-slate-800 border border-orange-900/20 rounded-xl px-6 py-3">
            <div className="text-orange-400 font-bold text-lg">
              💰 {credits} Credits
            </div>
            <div className="text-slate-500 text-sm">
              ({Math.floor(credits / 10)} queries left)
            </div>
            <Link 
              href="/get-credits"
              className="px-4 py-2 bg-orange-600 hover:bg-orange-500 rounded-lg text-sm font-semibold transition"
            >
              Get More
            </Link>
          </div>
        </div>

        <div className="mb-8 space-y-6 min-h-[400px]">
          {messages.length === 0 ? (
            <div className="text-center py-16">
              <div className="text-6xl mb-6">🏈</div>
              <p className="text-slate-400 text-xl mb-4">Ask your first NFL question!</p>
              <p className="text-slate-500 text-sm mb-6">Each query costs 10 credits</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  "Who should I bet on this week?",
                  "What's the best value play Sunday?",
                  "Analyze the Lions vs Bears game",
                  "Which unders look good this week?"
                ].map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => setQuery(suggestion)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition border border-orange-900/20 hover:border-orange-500/50"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                {msg.role === 'user' ? (
                  <div className="inline-block bg-orange-600 text-white px-6 py-3 rounded-2xl max-w-2xl">
                    {msg.content}
                  </div>
                ) : (
                  <div className={`inline-block ${msg.isError ? 'bg-red-900/20 border-red-500/50' : 'bg-slate-800 border-orange-900/20'} border px-6 py-4 rounded-2xl max-w-4xl text-left`}>
                    {msg.models && (
                      <div className="text-xs text-slate-500 mb-3 font-mono">
                        {msg.models.join(' + ')}
                      </div>
                    )}
                    <div className="prose prose-invert prose-orange max-w-none">
                      <ReactMarkdown
                        components={{
                          h2: ({node, ...props}) => <h2 className="text-xl font-bold text-orange-400 mt-4 mb-2" {...props} />,
                          h3: ({node, ...props}) => <h3 className="text-lg font-bold text-orange-300 mt-3 mb-2" {...props} />,
                          strong: ({node, ...props}) => <strong className="text-orange-400 font-semibold" {...props} />,
                          p: ({node, ...props}) => <p className="mb-3 leading-relaxed" {...props} />,
                          ul: ({node, ...props}) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
                          ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}

          {isAsking && (
            <div className="text-left">
              <div className="inline-block bg-slate-800 border border-orange-900/20 px-6 py-4 rounded-2xl">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  <span className="ml-2 text-slate-400">Analyzing NFL data...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="sticky bottom-0 bg-slate-950/90 backdrop-blur-sm py-6 border-t border-orange-900/20">
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Ask about any NFL game, player, or betting angle..."
              disabled={isAsking}
              className="flex-1 px-6 py-4 bg-slate-900 border border-orange-900/20 rounded-xl focus:border-orange-500 focus:outline-none text-white placeholder-slate-500 disabled:opacity-50"
            />
            <button
              onClick={handleAsk}
              disabled={!query.trim() || isAsking || credits < 10}
              className="px-8 py-4 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-xl font-bold transition shadow-lg shadow-orange-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAsking ? 'Asking...' : credits < 10 ? 'No Credits' : 'Ask'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
