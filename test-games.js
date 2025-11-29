const { createClient } = require('@supabase/supabase-js')
require('dotenv').config({ path: '.env.local' })

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

async function checkGames() {
  console.log('Checking games_raw table...')
  const { data: games, error } = await supabase
    .from('games_raw')
    .select('*')
    .order('game_time', { ascending: true })
    .limit(5)
  
  if (error) {
    console.error('Error:', error)
  } else {
    console.log('Found', games.length, 'games:')
    console.log(JSON.stringify(games, null, 2))
  }
}

checkGames()
