import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    
    const { data, error } = await supabase
      .from('ai_outputs')
      .select(`
        *,
        games_raw!inner(*)
      `)
      .eq('game_id', id)
      .single()

    if (error) throw error
    if (!data) {
      return NextResponse.json({ error: 'Game not found' }, { status: 404 })
    }

    return NextResponse.json({ game: data })
  } catch (error) {
    console.error('Error fetching game:', error)
    return NextResponse.json({ error: 'Failed to fetch game' }, { status: 500 })
  }
}
