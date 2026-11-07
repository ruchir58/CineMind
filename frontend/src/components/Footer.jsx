import React from 'react';
import { Film, Sparkles, Brain, Cpu, ShieldCheck } from 'lucide-react';

export default function Footer({ onNavigate }) {
  return (
    <footer className="mt-24 border-t border-white/5 bg-[#07090c] text-zinc-400 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        {/* Brand */}
        <div className="md:col-span-2 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
              <Film className="w-4 h-4" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Cine<span className="text-indigo-400">Mind</span>
            </span>
          </div>
          <p className="text-sm text-zinc-400 max-w-md leading-relaxed">
            AI-powered discovery platform connecting your mood, curiosities and cinematic taste
            to unforgettable stories. Built with dual ML & natural language embedding engines.
          </p>
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Instant Access: No accounts, no passwords, no personal tracking.</span>
          </div>
        </div>

        {/* Discovery engines */}
        <div className="space-y-3">
          <h4 className="text-xs uppercase font-semibold text-zinc-200 tracking-wider">
            Recommendation Engines
          </h4>
          <ul className="space-y-2 text-sm">
            <li>
              <button 
                onClick={() => onNavigate('smart')}
                className="hover:text-white transition-colors flex items-center gap-2"
              >
                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                <span>TF-IDF Smart Recommender</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => onNavigate('ai')}
                className="hover:text-white transition-colors flex items-center gap-2"
              >
                <Brain className="w-3.5 h-3.5 text-indigo-400" />
                <span>Semantic AI Prompt Finder</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => onNavigate('explore')}
                className="hover:text-white transition-colors flex items-center gap-2"
              >
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                <span>Curated Catalogue Browse</span>
              </button>
            </li>
          </ul>
        </div>

        {/* Attribution & Legal */}
        <div className="space-y-3">
          <h4 className="text-xs uppercase font-semibold text-zinc-200 tracking-wider">
            TMDB Attribution
          </h4>
          <p className="text-xs text-zinc-400 leading-relaxed">
            This product uses the TMDB API but is not endorsed or certified by TMDB. Movie and TV show posters, metadata, and cast details are provided under TMDB terms.
          </p>
          <div className="pt-1">
            <span className="text-[11px] px-2 py-1 rounded bg-[#131720] border border-white/5 text-zinc-400">
              TMDB API v3 Integrated
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-400 gap-4">
        <p>© {new Date().getFullYear()} CineMind. Crafted with React, FastAPI & SentenceTransformers.</p>
        <p className="text-zinc-400">Discover Stories Beyond Imagination.</p>
      </div>
    </footer>
  );
}

