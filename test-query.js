const { createClient } = require('@supabase/supabase-js')
require('dotenv').config({ path: '.env.local' })

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

async function test() {
  console.log('Testing the exact query from your API route...\n')
  
  const { data, error } = await supabase
    .from('ai_outputs')
    .select(`
      *,
      games_raw!inner(*)
    `)
    .eq('game_id', '401671890')
    .single()

  console.log('Result:', data)
  console.log('Error:', error)
}

test()
