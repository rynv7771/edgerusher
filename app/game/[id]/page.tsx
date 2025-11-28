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
      <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black text-white">
        <div className="container mx-auto px-4 py-20 text-center">
          <div className="text-xl">Loading game analysis...</div>
        </div>
      </div>
    )
  }

  if (!game) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black text-white">
        <div className="container mx-auto px-4 py-20 text-center">
          <div className="text-xl mb-4">Game not found</div>
          <Link href="/" className="text-blue-400 hover:text-blue-300">
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
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black text-white">
      <header className="border-b border-gray-800">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-3xl">🥾</span>
            <span className="text-2xl font-bold">Betting Boots</span>
          </Link>
          <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition">
            Sign In
          </button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <Link href="/" className="text-blue-400 hover:text-blue-300 mb-6 inline-block">
          ← Back to all games
        </Link>

        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-8 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="text-sm text-gray-400 mb-2">Week {game.games_raw.week}</div>
              <h1 className="text-4xl font-bold mb-2">
                {game.games_raw.raw_json.away_team.name}
                <span className="text-gray-500 mx-3">@</span>
                {game.games_raw.raw_json.home_team.name}
              </h1>
              <p className="text-gray-400">
                {gameTime.toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit'
                })} {timezoneName}
              </p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/50 rounded-lg flex items-center justify-between">
            <div>
              <div className="font-bold text-lg">Ready to place your bet?</div>
            </div>
            <a 
              href="https://sportsbook.draftkings.com/" 
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-bold transition whitespace-nowrap"
            >
              Place Bet →
            </a>
          </div>
        </div>

        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/50 rounded-lg p-6 mb-6">
          <div className="text-sm text-blue-400 font-medium mb-2">💡 TOP INSIGHT</div>
          <p className="text-xl font-medium">{game.top_insight}</p>
        </div>

        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 mb-6">
          <div className="text-sm text-gray-400 font-medium mb-2">AI PICK</div>
          <p className="text-2xl font-bold text-blue-400">{game.predicted_line}</p>
        </div>

        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Game Summary</h2>
          <p className="text-gray-300 leading-relaxed">{game.summary}</p>
        </div>

        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Betting Angles</h2>
          <div className="space-y-3">
            {game.angles.map((angle, index) => (
              <div key={index} className="flex gap-3">
                <span className="text-blue-400 font-bold">{index + 1}.</span>
                <p className="text-gray-300">{angle}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Predicted Line</div>
            <div className="text-2xl font-bold">{game.predicted_line}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Predicted Total</div>
            <div className="text-2xl font-bold">{game.predicted_total}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Injury Impact</div>
            <div className="text-xl font-medium">{game.injury_impact}</div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 mb-6">
          <h2 className="text-xl font-bold mb-6">Team Strength Comparison</h2>

          <div className="mb-6">
            <div className="text-sm text-gray-400 mb-3">{game.games_raw.raw_json.home_team.name}</div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Offense</span>
                  <span className="font-medium">{game.team_strength.home_offense}/100</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${game.team_strength.home_offense}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Defense</span>
                  <span className="font-medium">{game.team_strength.home_defense}/100</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${game.team_strength.home_defense}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-400 mb-3">{game.games_raw.raw_json.away_team.name}</div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Offense</span>
                  <span className="font-medium">{game.team_strength.away_offense}/100</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${game.team_strength.away_offense}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Defense</span>
                  <span className="font-medium">{game.team_strength.away_defense}/100</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${game.team_strength.away_defense}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold mb-2">Ready to Place Your Bet?</h3>
          <p className="mb-6 opacity-90">Use our analysis to make informed betting decisions</p>
          <a 
            href="https://sportsbook.draftkings.com/" 
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-8 py-3 bg-white text-green-600 hover:bg-gray-100 rounded-lg font-bold transition"
          >
            Place Bet →
          </a>
        </div>
      </div>
    </div>
  )
}
