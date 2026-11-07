import React, { useState, useEffect } from 'react';
import { SlidersHorizontal, Plus, X, Search, Sparkles, Filter, AlertCircle, Info } from 'lucide-react';
import { searchMedia, generateSmartRecommendations, fetchGenres } from '../services/api';
import MediaCard from '../components/MediaCard';
import ExplanationBadge from '../components/ExplanationBadge';

export default function SmartRecommendationsPage({ onSelectMedia }) {
  const [selectedTitles, setSelectedTitles] = useState(['Inception', 'Interstellar', 'The Prestige']);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // Filters
  const [mediaType, setMediaType] = useState('all');
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [availableGenres, setAvailableGenres] = useState([]);
  const [minRating, setMinRating] = useState(7.0);
  const [minYear, setMinYear] = useState('');
  const [maxYear, setMaxYear] = useState('');
  const [topN, setTopN] = useState(10);

  // State
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [hasGenerated, setHasGenerated] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const loadGenres = async () => {
      try {
        const data = await fetchGenres();
        setAvailableGenres(data);
      } catch (err) {
        console.error('Failed to load genres:', err);
      }
    };
    loadGenres();
  }, []);

  // Search autocomplete for adding titles
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

  const addTitle = (title) => {
    if (!selectedTitles.includes(title)) {
      setSelectedTitles([...selectedTitles, title]);
    }
    setSearchQuery('');
    setSearchResults([]);
  };

  const removeTitle = (titleToRemove) => {
    setSelectedTitles(selectedTitles.filter((t) => t !== titleToRemove));
  };

  const toggleGenre = (genreName) => {
    if (selectedGenres.includes(genreName)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genreName));
    } else {
      setSelectedGenres([...selectedGenres, genreName]);
    }
  };

  const handleGenerate = async () => {
    if (selectedTitles.length === 0) {
      setErrorMsg('Please select at least one favourite title.');
      return;
    }
    setErrorMsg('');
    setLoading(true);
    setHasGenerated(true);

    try {
      const payload = {
        selected_titles: selectedTitles,
        media_type: mediaType,
        genres: selectedGenres.length > 0 ? selectedGenres : null,
        min_rating: minRating > 0 ? parseFloat(minRating) : null,
        min_year: minYear ? parseInt(minYear) : null,
        max_year: maxYear ? parseInt(maxYear) : null,
        top_n: topN
      };

      const res = await generateSmartRecommendations(payload);
      setRecommendations(res.recommendations || []);
    } catch (err) {
      console.error('Error generating recommendations:', err);
      setErrorMsg('Failed to calculate recommendations. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pt-24 sm:pt-28 pb-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
      {/* Page Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>Content-Based Feature Vectors</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          Smart Recommendation Engine
        </h1>
        <p className="text-sm sm:text-base text-zinc-400 leading-relaxed">
          Select one or multiple movies and shows you love. Our algorithm analyzes their plot, cast, directors, keywords, and narrative motifs to uncover hidden gems.
        </p>
      </div>

      {/* Main Configuration Card */}
      <div className="bg-[#10141d] border border-white/5 rounded-3xl p-6 sm:p-8 space-y-8 shadow-xl">
        {/* Step 1: Select Favourite Titles */}
        <div className="space-y-4">
          <label className="block text-sm uppercase tracking-wider font-bold text-zinc-300">
            1. Select Your Favourite Titles ({selectedTitles.length})
          </label>

          {/* Autocomplete Input */}
          <div className="relative">
            <div className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-[#141822] border border-white/10 focus-within:border-indigo-500 transition-colors">
              <Search className="w-5 h-5 text-zinc-500" />
              <input
                type="text"
                placeholder="Search to add movies or TV shows (e.g. Inception, Breaking Bad, Dark...)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-transparent text-white placeholder-zinc-500 text-sm focus:outline-none"
              />
              {isSearching && (
                <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              )}
            </div>

            {/* Dropdown Results */}
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 z-30 mt-2 bg-[#141822] border border-white/10 rounded-2xl shadow-2xl max-h-60 overflow-y-auto p-2 divide-y divide-white/5">
                {searchResults.map((item) => (
                  <div
                    key={`${item.media_type}-${item.id}`}
                    onClick={() => addTitle(item.title)}
                    className="flex items-center justify-between p-2.5 rounded-xl hover:bg-white/5 cursor-pointer text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-white font-medium">{item.title}</span>
                      <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-white/10 text-zinc-400">
                        {item.media_type}
                      </span>
                    </div>
                    <Plus className="w-4 h-4 text-indigo-400" />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Selected Title Chips */}
          <div className="flex flex-wrap gap-2 pt-2">
            {selectedTitles.map((title) => (
              <span
                key={title}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-indigo-950/60 border border-indigo-500/30 text-indigo-200 text-xs sm:text-sm font-medium shadow-sm"
              >
                <span>{title}</span>
                <button
                  onClick={() => removeTitle(title)}
                  className="p-0.5 rounded-full hover:bg-white/10 text-zinc-400 hover:text-white transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Step 2: Fine-Tuning Filters */}
        <div className="space-y-6 pt-6 border-t border-white/5">
          <label className="block text-sm uppercase tracking-wider font-bold text-zinc-300 flex items-center gap-2">
            <Filter className="w-4 h-4 text-indigo-400" />
            <span>2. Optional Filters & Constraints</span>
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Media Type Toggle */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-zinc-400">Media Type</span>
              <div className="flex rounded-xl bg-[#141822] p-1 border border-white/5">
                {[
                  { id: 'all', label: 'All' },
                  { id: 'movie', label: 'Movies' },
                  { id: 'tv', label: 'TV Shows' },
                ].map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setMediaType(type.id)}
                    className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                      mediaType === type.id
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'text-zinc-400 hover:text-white'
                    }`}
                  >
                    {type.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Minimum Rating Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold text-zinc-400">
                <span>Minimum Rating</span>
                <span className="text-amber-400">★ {minRating.toFixed(1)} / 10</span>
              </div>
              <input
                type="range"
                min="0"
                max="9"
                step="0.5"
                value={minRating}
                onChange={(e) => setMinRating(parseFloat(e.target.value))}
                className="w-full accent-indigo-500 bg-[#141822] rounded-lg h-2"
              />
            </div>

            {/* Year Range */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-zinc-400">Release Year Range</span>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  placeholder="Min (e.g. 2000)"
                  value={minYear}
                  onChange={(e) => setMinYear(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-xl bg-[#141822] border border-white/5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                />
                <span className="text-zinc-500">-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={maxYear}
                  onChange={(e) => setMaxYear(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-xl bg-[#141822] border border-white/5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Recommendation Count Selector */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-zinc-400">Results Count</span>
              <select
                value={topN}
                onChange={(e) => setTopN(parseInt(e.target.value))}
                className="w-full px-3 py-2 rounded-xl bg-[#141822] border border-white/5 text-xs font-semibold text-white focus:outline-none focus:border-indigo-500"
              >
                <option value={5}>5 Recommendations</option>
                <option value={10}>10 Recommendations</option>
                <option value={15}>15 Recommendations</option>
                <option value={20}>20 Recommendations</option>
              </select>
            </div>
          </div>

          {/* Genre Multi-select */}
          {availableGenres.length > 0 && (
            <div className="space-y-2 pt-2">
              <span className="text-xs font-semibold text-zinc-400">Filter by Specific Genres (Optional)</span>
              <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-1">
                {availableGenres.map((g) => {
                  const isSelected = selectedGenres.includes(g.name);
                  return (
                    <button
                      key={g.id}
                      onClick={() => toggleGenre(g.name)}
                      className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                        isSelected
                          ? 'bg-indigo-600 border-indigo-500 text-white'
                          : 'bg-[#141822] border-white/5 text-zinc-400 hover:text-white'
                      }`}
                    >
                      {g.name}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Generate Button & Error feedback */}
        <div className="pt-4 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <Info className="w-4 h-4 text-zinc-400" />
            <span>Similarity scores represent mathematical feature overlap, not guarantee of subjective taste.</span>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || selectedTitles.length === 0}
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-600 disabled:opacity-50 text-white font-bold text-sm shadow-glow flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Computing Similarities...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Recommendations</span>
              </>
            )}
          </button>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Results Section */}
      {hasGenerated && (
        <div className="space-y-6 pt-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span>Recommended For You ({recommendations.length})</span>
            </h2>
          </div>

          {recommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {recommendations.map((rec) => (
                <div
                  key={`${rec.media.media_type}-${rec.media.id}`}
                  className="bg-[#10141d] border border-white/5 rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row gap-5 hover:border-indigo-500/30 transition-colors"
                >
                  <div className="w-full sm:w-44 shrink-0">
                    <MediaCard
                      item={rec.media}
                      similarityScore={rec.similarity_score}
                      onClick={onSelectMedia}
                    />
                  </div>
                  <div className="flex-1 flex flex-col justify-between gap-4">
                    <ExplanationBadge
                      explanation={rec.explanation}
                      title={rec.media.title}
                    />
                    <button
                      onClick={() => onSelectMedia(rec.media)}
                      className="w-full py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-zinc-300 hover:text-white transition-colors"
                    >
                      View Full Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center text-zinc-500 bg-[#10141d] rounded-3xl border border-white/5">
              <p className="text-base font-semibold text-zinc-300">No matching recommendations found.</p>
              <p className="text-xs text-zinc-500 mt-1">Try relaxing filters like minimum rating or genre constraints.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

