import GamesList from './components/GamesList'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-orange-900/20 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <img
              src="/boot-icon.png"
              alt="Betting Boots"
              className="h-12 w-auto"
            />
          </Link>
          <button className="px-8 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 rounded-lg font-bold transition shadow-lg shadow-orange-500/20">
            Sign In
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="py-24 text-center">
        <div className="container mx-auto px-4">
          <div className="inline-block mb-6 px-6 py-2 bg-orange-500/10 border border-orange-500/20 rounded-full">
            <span className="text-orange-400 font-semibold">⚡ AI-Powered Analysis</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-black mb-6 bg-gradient-to-r from-orange-400 via-yellow-400 to-orange-500 bg-clip-text text-transparent">
            Smarter NFL Betting
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Get AI-powered insights, betting angles, and predictions for every NFL game.
            <span className="text-orange-400"> Make smarter bets.</span>
          </p>
        </div>
      </section>

      {/* Games List */}
      <section className="py-16 bg-gradient-to-b from-slate-900/50 to-transparent">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="flex items-center gap-3 mb-10">
            <div className="h-1 w-12 bg-gradient-to-r from-orange-500 to-yellow-500"></div>
            <h2 className="text-4xl font-black">This Week's Games</h2>
          </div>
          <GamesList />
        </div>
      </section>

      {/* Features */}
      <section className="py-24 border-t border-orange-900/20">
        <div className="container mx-auto px-4 max-w-5xl">
          <h2 className="text-4xl font-black text-center mb-16">
            Why <span className="text-orange-400">Betting Boots?</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 border border-orange-900/20 hover:border-orange-500/50 transition">
              <div className="text-5xl mb-6">🤖</div>
              <h3 className="text-2xl font-bold mb-3 text-orange-400">AI Analysis</h3>
              <p className="text-slate-400 leading-relaxed">Advanced AI analyzes every game with deep statistical insights</p>
            </div>
            <div className="p-8 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 border border-orange-900/20 hover:border-orange-500/50 transition">
              <div className="text-5xl mb-6">📊</div>
              <h3 className="text-2xl font-bold mb-3 text-orange-400">Key Angles</h3>
              <p className="text-slate-400 leading-relaxed">Discover betting edges and insights you'd otherwise miss</p>
            </div>
            <div className="p-8 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 border border-orange-900/20 hover:border-orange-500/50 transition">
              <div className="text-5xl mb-6">⚡</div>
              <h3 className="text-2xl font-bold mb-3 text-orange-400">Daily Updates</h3>
              <p className="text-slate-400 leading-relaxed">Fresh analysis every morning at 3 AM EST</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-orange-900/20 text-center text-slate-500">
        <p>© 2025 Betting Boots. AI-Powered NFL Analysis.</p>
      </footer>
    </div>
  )
}
