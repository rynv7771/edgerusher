import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  try {
    const now = new Date().toISOString()
    
    const { data, error } = await supabase
      .from('ai_outputs')
      .select(`
        *,
        games_raw!inner(*)
      `)
      .gte('games_raw.game_time', now)
      .order('games_raw(game_time)', { ascending: true })
      .limit(20)

    if (error) throw error

    // Transform nested data to flat structure
    const games = (data || []).map((item: any) => ({
      game_id: item.game_id,
      away_team: item.games_raw.away_team,
      home_team: item.games_raw.home_team,
      game_time: item.games_raw.game_time,
      venue: item.games_raw.venue,
      ai_lean: item.ai_lean,
      top_insight: item.top_insight,
      predicted_total: item.predicted_total,
      summary: item.summary,
      angles: item.angles,
      predicted_line: item.predicted_line,
      team_strength: item.team_strength,
      injury_impact: item.injury_impact,
      confidence_score: item.confidence_score
    }))

    return NextResponse.json(games)
  } catch (error) {
    console.error('Error fetching games:', error)
    return NextResponse.json({ error: 'Failed to fetch games' }, { status: 500 })
  }
}
