'use client'

import { useEffect, useState } from 'react'
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
  }
}

export default function GamesList() {
  const [games, setGames] = useState<Game[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/games')
      .then(res => res.json())
      .then(data => {
        setGames(data.games)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="text-center py-12">Loading games...</div>
  }

  if (games.length === 0) {
    return <div className="text-center py-12 text-gray-400">No upcoming games available.</div>
  }

  return (
    <div className="grid gap-6">
      {games.map(game => {
        const gameTime = new Date(game.games_raw.game_time + 'Z')
        const timezoneName = gameTime.toLocaleTimeString('en-US', { 
          timeZoneName: 'short' 
        }).split(' ').pop()
        
        // Clean up ai_lean - remove "Lean: " prefix if present
        const cleanPick = game.ai_lean.replace(/^Lean:\s*/i, '').trim()
        
        return (
          <div key={game.id} className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 hover:border-blue-500 transition">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-xl font-bold mb-2">
                  {game.games_raw.raw_json.away_team.name} @ {game.games_raw.raw_json.home_team.name}
                </h3>
                <p className="text-sm text-gray-400">
                  {gameTime.toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit'
                  })} {timezoneName}
                </p>
              </div>
            </div>

            <div className="mb-4">
              <p className="text-lg font-medium text-blue-400 mb-2">
                💡 {game.top_insight}
              </p>
            </div>

            <div className="flex gap-4 text-sm flex-wrap mb-4">
              <div>
                <span className="text-gray-400">AI Pick:</span>
                <span className="ml-2 font-medium">{cleanPick}</span>
              </div>
              <div>
                <span className="text-gray-400">Predicted Total:</span>
                <span className="ml-2 font-medium">{game.predicted_total}</span>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-700 flex gap-3">
              <Link
                href={`/game/${game.game_id}`}
                className="flex-1 text-center py-2 text-blue-400 hover:text-blue-300 font-medium transition"
              >
                View Full Analysis →
              </Link>
              <a 
                href="https://sportsbook.draftkings.com/" 
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition whitespace-nowrap"
              >
                Place Bet
              </a>
            </div>
          </div>
        )
      })}
    </div>
  )
}
