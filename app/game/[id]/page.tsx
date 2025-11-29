'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface Game {
  id: number
  game_id: string
  top_insight: string
  summary: string
  ai_lean: string
  angles: string[]
  predicted_line: string
  predicted_total: string
  team_strength: {
    home_offense: string
    home_defense: string
    away_offense: string
    away_defense: string
  }
  injury_impact: string
  confidence_score: string
  games_raw: {
    raw_json: {
      away_team: {
        name: string
      }
      home_team: {
        name: string
      }
    }
    game_time: string
    week: number
  }
}

export default function GameDetailPage() {
  const params = useParams()
  const [game, setGame] = useState<Game | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      fetch(`/api/game/${params.id}`)
        .then(res => res.json())
        .then(data => {
          if (data.game) {
            setGame(data.game)
          }
          setLoading(false)
        })
        .catch(() => setLoading(false))
    }
  }, [params.id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
        <div className="container mx-auto px-4 py-20 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500 mx-auto"></div>
        </div>
      </div>
    )
  }

  if (!game) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
        <div className="container mx-auto px-4 py-20 text-center">
          <div className="text-xl mb-4">Game not found</div>
          <Link href="/" className="text-orange-400 hover:text-orange-300">
            ← Back to home
          </Link>
        </div>
      </div>
    )
  }

  const gameTime = new Date(game.games_raw.game_time + 'Z')
  const timezoneName = gameTime.toLocaleTimeString('en-US', {
    timeZoneName: 'short'
  }).split(' ').pop()

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-orange-900/20 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <img
              src="/boot-icon.png"
              alt="Betting Boots"
              className="h-12 w-auto"
            />
          </Link>
          <button className="px-8 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-lg font-bold transition shadow-lg shadow-orange-500/20">
            Sign In
          </button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <Link href="/" className="text-orange-400 hover:text-orange-300 mb-8 inline-flex items-center gap-2 font-semibold">
          ← Back to all games
        </Link>

        {/* Game Header */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700/50 p-8 mb-6">
          <div className="text-sm text-slate-500 mb-2">Week {game.games_raw.week}</div>
          <h1 className="text-4xl md:text-5xl font-black mb-4">
            {game.games_raw.raw_json.away_team.name}
            <span className="text-slate-600 mx-3">@</span>
            {game.games_raw.raw_json.home_team.name}
          </h1>
          <p className="text-slate-400 text-lg mb-6">
            📅 {gameTime.toLocaleDateString('en-US', {
              weekday: 'long',
              month: 'long',
              day: 'numeric'
            })} at {gameTime.toLocaleTimeString('en-US', {
              hour: 'numeric',
              minute: '2-digit'
            })} {timezoneName}
          </p>

          {/* CTA Box */}
          <div className="p-6 bg-gradient-to-r from-orange-600/20 to-orange-500/20 border border-orange-500/50 rounded-xl flex flex-col md:flex-row items-stretch md:items-center gap-4">
            <div>
              <div className="font-bold text-xl text-white">Ready to place your bet?</div>
              <div className="text-orange-300 text-sm">Use our AI analysis to bet smarter</div>
            </div>
            <a
              href="https://sportsbook.draftkings.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-lg font-bold transition shadow-lg shadow-orange-500/20 w-full md:w-auto"
            >
              Place Bet →
            </a>
          </div>
        </div>

        {/* Top Insight */}
        <div className="bg-slate-950/50 rounded-xl border border-orange-900/20 p-6 mb-6">
          <div className="flex items-start gap-3 mb-3">
            <span className="text-3xl">💡</span>
            <div className="text-sm text-orange-400 font-semibold uppercase tracking-wide">Top Insight</div>
          </div>
          <p className="text-xl text-slate-200 leading-relaxed">{game.top_insight}</p>
        </div>

        {/* AI Pick & Stats */}
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <div className="bg-slate-950/50 rounded-xl border border-slate-700/50 p-6">
            <div className="text-xs text-slate-500 uppercase font-semibold mb-2">AI Pick</div>
            <div className="text-2xl font-bold text-orange-400">{game.ai_lean}</div>
          </div>
          <div className="bg-slate-950/50 rounded-xl border border-slate-700/50 p-6">
            <div className="text-xs text-slate-500 uppercase font-semibold mb-2">Predicted Total</div>
            <div className="text-2xl font-bold text-yellow-400">{game.predicted_total}</div>
          </div>
          <div className="bg-slate-950/50 rounded-xl border border-slate-700/50 p-6">
            <div className="text-xs text-slate-500 uppercase font-semibold mb-2">Confidence</div>
            <div className="text-xl font-bold text-slate-200">{game.confidence_score}</div>
          </div>
        </div>

        {/* Summary */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700/50 p-8 mb-6">
          <h2 className="text-2xl font-black mb-4 flex items-center gap-3">
            <div className="h-1 w-8 bg-gradient-to-r from-orange-500 to-yellow-500"></div>
            Game Summary
          </h2>
          <p className="text-slate-300 leading-relaxed text-lg">{game.summary}</p>
        </div>

        {/* Betting Angles */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700/50 p-8 mb-6">
          <h2 className="text-2xl font-black mb-6 flex items-center gap-3">
            <div className="h-1 w-8 bg-gradient-to-r from-orange-500 to-yellow-500"></div>
            Betting Angles
          </h2>
          <div className="space-y-4">
            {game.angles.map((angle, index) => (
              <div key={index} className="flex gap-4 p-4 bg-slate-950/50 rounded-lg border border-slate-700/30">
                <span className="text-orange-400 font-bold text-lg flex-shrink-0">{index + 1}.</span>
                <p className="text-slate-300 leading-relaxed">{angle}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Team Strength */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700/50 p-8 mb-6">
          <h2 className="text-2xl font-black mb-8 flex items-center gap-3">
            <div className="h-1 w-8 bg-gradient-to-r from-orange-500 to-yellow-500"></div>
            Team Strength Comparison
          </h2>

          <div className="mb-8">
            <div className="text-lg font-bold mb-4 text-orange-400">{game.games_raw.raw_json.home_team.name}</div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Offense</span>
                  <span className="font-bold text-slate-200">{game.team_strength.home_offense}/100</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-orange-500 to-yellow-500 h-3 rounded-full transition-all"
                    style={{ width: `${game.team_strength.home_offense}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Defense</span>
                  <span className="font-bold text-slate-200">{game.team_strength.home_defense}/100</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full transition-all"
                    style={{ width: `${game.team_strength.home_defense}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="text-lg font-bold mb-4 text-orange-400">{game.games_raw.raw_json.away_team.name}</div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Offense</span>
                  <span className="font-bold text-slate-200">{game.team_strength.away_offense}/100</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-orange-500 to-yellow-500 h-3 rounded-full transition-all"
                    style={{ width: `${game.team_strength.away_offense}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Defense</span>
                  <span className="font-bold text-slate-200">{game.team_strength.away_defense}/100</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full transition-all"
                    style={{ width: `${game.team_strength.away_defense}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="bg-gradient-to-r from-orange-600 to-orange-500 rounded-2xl p-8 text-center shadow-xl shadow-orange-500/20">
          <h3 className="text-3xl font-black mb-3">Ready to Place Your Bet?</h3>
          <p className="mb-6 text-orange-100 text-lg">Use our AI analysis to make smarter betting decisions</p>
          <a
            href="https://sportsbook.draftkings.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-10 py-4 bg-white text-orange-600 hover:bg-slate-100 rounded-lg font-bold transition text-lg shadow-lg"
          >
            Place Bet on DraftKings →
          </a>
        </div>
      </div>
    </div>
  )
}
