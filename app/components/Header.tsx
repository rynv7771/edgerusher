'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function Header() {
  const [user, setUser] = useState<any>(null)
  const [showMenu, setShowMenu] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Check current user
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/')
    setShowMenu(false)
  }

  return (
    <header className="border-b border-orange-900/20 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
          <img
            src="/boot-icon.png"
            alt="EdgeRusher"
            className="h-12 w-auto"
          />
        </Link>

        {user ? (
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-lg transition shadow-lg shadow-orange-500/20"
              aria-label="Menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {showMenu && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 mt-2 w-64 bg-slate-900 border border-orange-900/20 rounded-lg shadow-xl overflow-hidden z-50">
                  <div className="px-6 py-3 text-sm text-slate-400 border-b border-orange-900/20">
                    Signed in as:<br/>
                    <span className="text-white font-medium">{user.email}</span>
                  </div>
                  <Link
                    href="/pro-chat"
                    onClick={() => setShowMenu(false)}
                    className="block px-6 py-3 hover:bg-orange-500/10 transition border-b border-orange-900/20"
                  >
                    <span className="text-orange-400 font-semibold">⚡ Pro Chat</span>
                  </Link>
                  <Link
                    href="/account"
                    onClick={() => setShowMenu(false)}
                    className="block px-6 py-3 hover:bg-orange-500/10 transition border-b border-orange-900/20"
                  >
                    Account Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-6 py-3 hover:bg-red-500/10 text-red-400 transition"
                  >
                    Log Out
                  </button>
                </div>
              </>
            )}
          </div>
        ) : (
          <Link
            href="/auth/signin"
            className="px-8 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-lg font-bold transition shadow-lg shadow-orange-500/20"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  )
}
