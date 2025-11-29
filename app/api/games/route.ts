import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  try {
    // Get current time in UTC (ESPN times are in UTC)
    const now = new Date().toISOString()
    
    const { data, error } = await supabase
      .from('ai_outputs')
      .select(`
        *,
        games_raw!inner(*)
      `)
      .gte('games_raw.game_time', now) // Only future games
      .order('games_raw(game_time)', { ascending: true })
      .limit(20)

    if (error) throw error

    return NextResponse.json(data || [])
  } catch (error) {
    console.error('Error fetching games:', error)
    return NextResponse.json({ error: 'Failed to fetch games' }, { status: 500 })
  }
}
