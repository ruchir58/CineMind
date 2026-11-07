import React, { useState, useEffect } from 'react';
import { Sparkles, Compass, SlidersHorizontal, ArrowRight, Star, Flame, Trophy, Film, Tv, Play } from 'lucide-react';
import { fetchTrending, fetchPopular, fetchTopRated, fetchGenres } from '../services/api';
import MediaCard from '../components/MediaCard';

export default function HomePage({ onNavigate, onSelectMedia }) {
  const [trending, setTrending] = useState([]);
  const [popularShows, setPopularShows] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [trendData, popTvData, topData, genreData] = await Promise.all([
          fetchTrending('movie'),
          fetchPopular('tv'),
          fetchTopRated('movie'),
          fetchGenres(),
        ]);
        setTrending(trendData.slice(0, 8));
        setPopularShows(popTvData.slice(0, 8));
        setTopRated(topData.slice(0, 8));
        setGenres(genreData.slice(0, 10));
      } catch (err) {
        console.error('Failed to load home data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadHomeData();
  }, []);

  return (
    <div className="space-y-16 sm:space-y-24 pb-12">
      {/* Hero Section */}
      <section className="relative pt-24 sm:pt-32 pb-16 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-600/15 rounded-full blur-[120px] pointer-events-none" />
        
        <div className="relative max-w-4xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-950/50 border border-indigo-500/30 text-indigo-300 text-xs font-semibold backdrop-blur-md animate-in fade-in slide-in-from-bottom-2 duration-300">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Dual ML & Natural Language Discovery Engines</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.1]">
            Discover Stories <br />
            <span className="bg-gradient-to-r from-indigo-300 via-indigo-100 to-zinc-400 bg-clip-text text-transparent">
              Beyond Imagination.
            </span>
          </h1>

          <p className="text-base sm:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed font-normal">
            Your personal AI-powered guide to movies and television. Describe what you're in the mood for or let our algorithms map your cinematic taste.
          </p>

          {/* Main Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onNavigate('ai')}
              className="w-full sm:w-auto flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold text-sm shadow-glow transition-all duration-200 group"
            >
              <Sparkles className="w-4 h-4 text-indigo-200" />
              <span>Find Something to Watch</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={() => onNavigate('explore')}
              className="w-full sm:w-auto flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-2xl bg-[#141822] hover:bg-[#1c2230] text-zinc-200 hover:text-white font-semibold text-sm border border-white/5 transition-all duration-200"
            >
              <Compass className="w-4 h-4 text-zinc-400" />
              <span>Explore Movies</span>
            </button>
          </div>
        </div>
      </section>

      {/* AI Recommendation Feature Spotlight Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#121624] via-[#10141e] to-[#121624] border border-indigo-500/20 p-6 sm:p-10 shadow-2xl">
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-3 max-w-xl text-center md:text-left">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-400 text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Next-Gen Discovery</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Have a very specific mood in mind?
              </h2>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Describe it in plain language. Try prompts like: <br />
                <span className="italic text-indigo-300">"Suggest a TV show similar to Dark and Severance"</span> or <br />
                <span className="italic text-indigo-300">"I want a psychological thriller with an unpredictable ending."</span>
              </p>
            </div>

            <button
              onClick={() => onNavigate('ai')}
              className="shrink-0 flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-glow transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>Try AI Movie Finder</span>
            </button>
          </div>
        </div>
      </section>

      {/* Trending Movies Row */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-950/50 border border-indigo-500/20 text-indigo-400">
              <Flame className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                Trending Movies
              </h2>
              <p className="text-xs text-zinc-400">What cinema lovers are watching right now</p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('explore')}
            className="text-xs font-semibold text-zinc-400 hover:text-white flex items-center gap-1 transition-colors"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="aspect-[2/3] bg-white/5 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 sm:gap-6">
            {trending.map((item) => (
              <MediaCard
                key={`trend-${item.id}`}
                item={item}
                onClick={onSelectMedia}
              />
            ))}
          </div>
        )}
      </section>

      {/* Popular TV Shows Row */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-sky-950/50 border border-sky-500/20 text-sky-400">
              <Tv className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                Acclaimed TV Shows
              </h2>
              <p className="text-xs text-zinc-400">Critically praised binge-worthy television series</p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('explore')}
            className="text-xs font-semibold text-zinc-400 hover:text-white flex items-center gap-1 transition-colors"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 sm:gap-6">
          {popularShows.map((item) => (
            <MediaCard
              key={`tv-${item.id}`}
              item={item}
              onClick={onSelectMedia}
            />
          ))}
        </div>
      </section>

      {/* Top-Rated Masterpieces Row */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-950/50 border border-amber-500/20 text-amber-400">
              <Trophy className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                Top-Rated Masterpieces
              </h2>
              <p className="text-xs text-zinc-400">Highest rated stories of all time</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 sm:gap-6">
          {topRated.map((item) => (
            <MediaCard
              key={`top-${item.id}`}
              item={item}
              onClick={onSelectMedia}
            />
          ))}
        </div>
      </section>

      {/* Genre Browse Bar */}
      {genres.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
          <h3 className="text-sm uppercase font-bold tracking-wider text-zinc-400">
            Browse by Popular Genres
          </h3>
          <div className="flex flex-wrap gap-2">
            {genres.map((g) => (
              <button
                key={g.id}
                onClick={() => onNavigate('explore', { genre: g.name })}
                className="px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-[#121620] hover:bg-[#1a202c] text-zinc-300 hover:text-white border border-white/5 hover:border-indigo-500/30 transition-all"
              >
                {g.name}
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

