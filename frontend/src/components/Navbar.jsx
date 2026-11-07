import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Compass, SlidersHorizontal, Search, Film, X, Clapperboard, Tv } from 'lucide-react';
import { searchMedia } from '../services/api';

export default function Navbar({ currentTab, setCurrentTab, onSelectMedia }) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchInputRef = useRef(null);

  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const data = await searchMedia(searchQuery.trim());
        setSearchResults(data.results || []);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setIsSearching(false);
      }
    }, 280);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const navItems = [
    { id: 'home', label: 'Home', icon: Clapperboard },
    { id: 'smart', label: 'Smart Picks', icon: SlidersHorizontal },
    { id: 'ai', label: 'AI Finder', icon: Sparkles, highlight: true },
    { id: 'explore', label: 'Explore', icon: Compass },
  ];

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-40 glass-nav">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            {/* Logo */}
            <div 
              onClick={() => setCurrentTab('home')}
              className="flex items-center gap-3 cursor-pointer group"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-indigo-400 p-[1px] shadow-glow">
                <div className="w-full h-full bg-[#0d1117] rounded-[11px] flex items-center justify-center">
                  <Film className="w-5 h-5 text-indigo-400 group-hover:scale-110 transition-transform duration-300" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
                  Cine<span className="text-indigo-400">Mind</span>
                </span>
                <span className="text-[10px] tracking-wider text-zinc-400 uppercase font-medium">
                  AI Discovery
                </span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1.5 bg-[#12161f]/80 p-1.5 rounded-full border border-white/5">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setCurrentTab(item.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? item.highlight
                          ? 'bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-glow'
                          : 'bg-white/10 text-white'
                        : item.highlight
                        ? 'text-indigo-400 hover:text-indigo-300 hover:bg-indigo-950/30'
                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Right actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsSearchOpen(true)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl bg-[#141822] hover:bg-[#1c2230] text-zinc-400 hover:text-white text-sm border border-white/5 transition-all duration-200"
                title="Search movies & TV shows"
              >
                <Search className="w-4 h-4" />
                <span className="hidden sm:inline text-xs font-medium">Quick Search</span>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile bottom navigation */}
        <div className="md:hidden flex items-center justify-around py-2.5 px-3 bg-[#0d1017]/95 border-t border-white/5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`flex flex-col items-center gap-1 py-1 px-3 rounded-lg text-xs font-medium transition-colors ${
                  isActive ? 'text-indigo-400' : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Quick Search Overlay Modal */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/80 backdrop-blur-md">
          <div className="relative w-full max-w-2xl bg-[#11151e] border border-white/10 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            {/* Search Input Bar */}
            <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
              <Search className="w-5 h-5 text-indigo-400" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search movies, TV shows, actors, directors..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-transparent text-white placeholder-zinc-500 text-base focus:outline-none"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="text-zinc-500 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => setIsSearchOpen(false)}
                className="px-2 py-1 text-xs font-medium text-zinc-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-md"
              >
                ESC
              </button>
            </div>

            {/* Results container */}
            <div className="max-h-[60vh] overflow-y-auto p-3 divide-y divide-white/5">
              {isSearching ? (
                <div className="py-12 text-center text-zinc-500 flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                  <span>Searching catalogue...</span>
                </div>
              ) : searchResults.length > 0 ? (
                searchResults.map((item) => (
                  <div
                    key={`${item.media_type}-${item.id}`}
                    onClick={() => {
                      onSelectMedia(item);
                      setIsSearchOpen(false);
                    }}
                    className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 cursor-pointer transition-colors group"
                  >
                    <div className="w-12 h-16 rounded-md bg-[#181d28] overflow-hidden flex-shrink-0">
                      {item.poster_path ? (
                        <img
                          src={`https://image.tmdb.org/t/p/w200${item.poster_path}`}
                          alt={item.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-zinc-600">
                          {item.media_type === 'tv' ? <Tv className="w-5 h-5" /> : <Film className="w-5 h-5" />}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-white truncate group-hover:text-indigo-400 transition-colors">
                          {item.title}
                        </h4>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-zinc-400 uppercase font-bold">
                          {item.media_type}
                        </span>
                      </div>
                      <p className="text-xs text-zinc-400 mt-0.5 line-clamp-1">
                        {item.release_date ? item.release_date.substring(0, 4) : 'N/A'} • {item.genres?.join(', ') || 'Various'}
                      </p>
                    </div>
                    {item.vote_average > 0 && (
                      <div className="text-xs font-semibold text-amber-400 px-2 py-1 rounded bg-amber-400/10">
                        ★ {item.vote_average.toFixed(1)}
                      </div>
                    )}
                  </div>
                ))
              ) : searchQuery ? (
                <div className="py-12 text-center text-zinc-500">
                  No matching titles found for "{searchQuery}".
                </div>
              ) : (
                <div className="py-8 text-center text-xs text-zinc-500">
                  Type title, actor, or genre to discover movies and shows.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

