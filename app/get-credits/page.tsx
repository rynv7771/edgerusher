'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import Header from '../components/Header'

export default function GetCredits() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [purchasing, setPurchasing] = useState(false)
  const [error, setError] = useState('')
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
    setLoading(false)
  }

  const packages = [
    {
      credits: 100,
      price: 1.00,
      popular: false,
      queries: 10,
      description: 'Perfect for trying Pro Chat'
    },
    {
      credits: 500,
      price: 4.50,
      popular: true,
      savings: '$0.50',
      queries: 50,
      description: 'Best value for regular use'
    },
    {
      credits: 1000,
      price: 8.00,
      popular: false,
      savings: '$2.00',
      queries: 100,
      description: 'Great for power users'
    },
    {
      credits: 2500,
      price: 18.00,
      popular: false,
      savings: '$7.00',
      queries: 250,
      description: 'Maximum value'
    }
  ]

  const handlePurchase = async (credits: number, price: number) => {
    setPurchasing(true)
    setError('')

    try {
      const response = await fetch('/api/create-credit-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          credits,
          amount: price,
          userId: user.id
        })
      })

      const data = await response.json()

      if (data.error) {
        throw new Error(data.error)
      }

      window.location.href = data.checkoutUrl
    } catch (err: any) {
      setError(err.message)
      setPurchasing(false)
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

      <div className="container mx-auto px-4 py-12 max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-black mb-4 bg-gradient-to-r from-orange-400 via-yellow-400 to-orange-500 bg-clip-text text-transparent">
            Get NFL Pro Credits
          </h1>
          <p className="text-slate-400 text-xl">
            Each Pro Chat query costs 10 credits. Choose your package:
          </p>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto mb-8 bg-red-900/20 border border-red-500/50 text-red-400 px-6 py-4 rounded-xl">
            {error}
          </div>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {packages.map((pkg, i) => (
            <div
              key={i}
              className={`relative bg-slate-800 border ${
                pkg.popular ? 'border-orange-500' : 'border-orange-900/20'
              } rounded-2xl p-6 hover:border-orange-500/50 transition`}
            >
              {pkg.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-orange-500 text-white px-4 py-1 rounded-full text-sm font-bold">
                  BEST VALUE
                </div>
              )}

              <div className="text-center mb-6">
                <div className="text-5xl font-black text-orange-400 mb-2">
                  {pkg.credits}
                </div>
                <div className="text-slate-400">credits</div>
                {pkg.savings && (
                  <div className="text-green-400 text-sm mt-1">
                    Save {pkg.savings}
                  </div>
                )}
              </div>

              <div className="text-center mb-6">
                <div className="text-3xl font-bold mb-2">
                  ${pkg.price.toFixed(2)}
                </div>
                <div className="text-slate-400 text-sm mb-4">
                  {pkg.queries} Pro Chat queries
                </div>
                <div className="text-slate-500 text-xs">
                  {pkg.description}
                </div>
              </div>

              <button
                onClick={() => handlePurchase(pkg.credits, pkg.price)}
                disabled={purchasing}
                className="w-full py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-xl font-bold transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {purchasing ? 'Processing...' : 'Purchase'}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center text-slate-400">
          <p className="mb-2">💳 Secure payment powered by Stripe</p>
          <p>Credits never expire. Use them anytime.</p>
        </div>
      </div>
    </div>
  )
}
