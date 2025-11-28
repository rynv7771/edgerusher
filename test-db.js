const { createClient } = require('@supabase/supabase-js')
require('dotenv').config({ path: '.env.local' })

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

async function test() {
  console.log('Checking games_raw...')
  const { data: games, error: gamesError } = await supabase
    .from('games_raw')
    .select('*')
    .eq('game_id', '401671890')
  console.log('games_raw:', games, gamesError)

  console.log('\nChecking ai_outputs...')
  const { data: ai, error: aiError } = await supabase
    .from('ai_outputs')
    .select('*')
    .eq('game_id', '401671890')
  console.log('ai_outputs:', ai, aiError)
}

test()
