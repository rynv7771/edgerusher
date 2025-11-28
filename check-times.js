const { createClient } = require('@supabase/supabase-js')
require('dotenv').config({ path: '.env.local' })

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

async function checkTimes() {
  const { data } = await supabase
    .from('games_raw')
    .select('game_id, game_time, raw_json')
    .limit(3)
  
  data.forEach(game => {
    console.log('\nGame:', game.raw_json.away_team.name, '@', game.raw_json.home_team.name)
    console.log('Stored game_time:', game.game_time)
    console.log('As Date object:', new Date(game.game_time))
  })
}

checkTimes()
