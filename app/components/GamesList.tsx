'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface Game {
  game_id: string
  away_team: { name: string; abbreviation: string }
  home_team: { name: string; abbreviation: string }
  game_time: string
  venue: string
  ai_lean: string
  top_insight: string
  predicted_total: string
}

export default function GamesList() {
  const [games, setGames] = useState<Game[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/games')
      .then(res => res.json())
      .then(data => {
        setGames(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to fetch games:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
      </div>
    )
  }

  if (games.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-4">🏈</div>
        <p className="text-xl text-slate-400">No games available yet. Check back soon!</p>
      </div>
    )
  }

  return (
    <div className="grid gap-6">
      {games.map((game) => {
        const gameTime = new Date(game.game_time + 'Z')
        const formattedTime = gameTime.toLocaleString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          timeZoneName: 'short'
        })

        const aiLean = game.ai_lean?.replace(/^Lean:\s*/i, '') || 'Analysis pending'

        return (
          <div
            key={game.game_id}
            className="group bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700/50 hover:border-orange-500/50 transition-all duration-300 overflow-hidden hover:shadow-xl hover:shadow-orange-500/10"
          >
            <div className="p-8">
              {/* Matchup */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex-1">
                  <div className="text-2xl font-bold text-slate-200 mb-1">
                    {game.away_team.name} <span className="text-slate-600">@</span> {game.home_team.name}
                  </div>
                  <div className="text-sm text-slate-500 flex items-center gap-2">
                    <span>📅 {formattedTime}</span>
                  </div>
                </div>
              </div>

              {/* AI Insight */}
              <div className="mb-6 p-4 bg-slate-950/50 rounded-xl border border-orange-900/20">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">💡</span>
                  <div className="flex-1">
                    <div className="text-sm text-orange-400 font-semibold mb-1">AI Insight</div>
                    <p className="text-slate-300 leading-relaxed">{game.top_insight}</p>
                  </div>
                </div>
              </div>

              {/* AI Pick & Total */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-700/50">
                  <div className="text-xs text-slate-500 uppercase font-semibold mb-1">AI Pick</div>
                  <div className="text-xl font-bold text-orange-400">{aiLean}</div>
                </div>
                <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-700/50">
                  <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Predicted Total</div>
                  <div className="text-xl font-bold text-yellow-400">{game.predicted_total || 'TBD'}</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Link
                  href={`/game/${game.game_id}`}
                  className="flex-1 py-3 px-6 bg-slate-800 hover:bg-slate-700 border border-slate-600 hover:border-orange-500/50 rounded-lg font-semibold text-center transition group-hover:border-orange-500/50"
                >
                  View Full Analysis →
                </Link>
                <button className="px-8 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-lg font-bold transition shadow-lg shadow-orange-500/20">
                  Place Bet
                </button>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
