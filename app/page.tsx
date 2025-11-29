import GamesList from './components/GamesList'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2">
            <img
              src="/logo.png"
              alt="Betting Boots"
              className="h-12 w-auto"
            />
          </Link>
          <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition">
            Sign In
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 text-center border-b border-gray-800">
        <div className="container mx-auto px-4">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            AI-Powered NFL Betting Analysis
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            AI-powered analysis for every NFL game. Get insights, angles, and predictions before you place your bets.
          </p>
        </div>
      </section>

      {/* Games List */}
      <section className="py-12">
        <div className="container mx-auto px-4 max-w-6xl">
          <h2 className="text-3xl font-bold mb-8">This Week's Games</h2>
          <GamesList />
        </div>
      </section>

      {/* Features */}
      <section className="py-20 border-t border-gray-800">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <h2 className="text-3xl font-bold mb-12">Why Betting Boots?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold mb-2">AI Analysis</h3>
              <p className="text-gray-400">Every game analyzed by advanced AI</p>
            </div>
            <div className="p-6">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-bold mb-2">Key Angles</h3>
              <p className="text-gray-400">Find betting edges you'd miss</p>
            </div>
            <div className="p-6">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-bold mb-2">Daily Updates</h3>
              <p className="text-gray-400">Fresh analysis every morning</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
