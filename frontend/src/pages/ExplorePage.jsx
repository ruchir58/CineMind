import React, { useState, useEffect } from 'react';
import { Compass, Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight, Film, Tv } from 'lucide-react';
import { fetchMovies, fetchTvShows, fetchGenres } from '../services/api';
import MediaCard from '../components/MediaCard';

export default function ExplorePage({ onSelectMedia, initialGenre = '' }) {
  const [mediaType, setMediaType] = useState('all');
  const [selectedGenre, setSelectedGenre] = useState(initialGenre);
  const [sortBy, setSortBy] = useState('popularity');
  const [searchFilter, setSearchFilter] = useState('');
  const [genres, setGenres] = useState([]);

  // Data
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadGenres = async () => {
      try {
        const data = await fetchGenres();
        setGenres(data);
      } catch (err) {
        console.error('Failed to load genres:', err);
      }
    };
    loadGenres();
  }, []);

  useEffect(() => {
    const loadCatalog = async () => {
      setLoading(true);
      try {
        let results = [];
        const params = {
          page,
          page_size: 24,
          genre: selectedGenre || undefined,
          sort_by: sortBy
        };

        if (mediaType === 'movie') {
          results = await fetchMovies(params);
        } else if (mediaType === 'tv') {
          results = await fetchTvShows(params);
        } else {
          const [m, t] = await Promise.all([
            fetchMovies({ ...params, page_size: 12 }),
            fetchTvShows({ ...params, page_size: 12 }),
          ]);
          results = [...m, ...t];
        }

        setItems(results);
      } catch (err) {
        console.error('Failed to load explore catalogue:', err);
      } finally {
        setLoading(false);
      }
    };

    loadCatalog();
  }, [mediaType, selectedGenre, sortBy, page]);

  // Client-side search filtering if user types in quick filter
  const filteredItems = items.filter((item) => {
    if (!searchFilter.trim()) return true;
    const q = searchFilter.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      (item.overview && item.overview.toLowerCase().includes(q))
    );
  });

  return (
    <div className="pt-24 sm:pt-28 pb-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 text-zinc-300 text-xs font-semibold mb-2">
            <Compass className="w-3.5 h-3.5 text-indigo-400" />
            <span>Curated Entertainment Catalogue</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Explore Films & Series
          </h1>
        </div>

        {/* Media Type Tabs */}
        <div className="flex rounded-xl bg-[#141824] p-1 border border-white/5 self-start">
          {[
            { id: 'all', label: 'All Media' },
            { id: 'movie', label: 'Movies' },
            { id: 'tv', label: 'TV Shows' },
          ].map((type) => (
            <button
              key={type.id}
              onClick={() => {
                setMediaType(type.id);
                setPage(1);
              }}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors ${
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

      {/* Control Bar: Search + Genre + Sort */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-[#10141e] p-4 rounded-2xl border border-white/5">
        {/* Search Filter */}
        <div className="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-[#141824] border border-white/5">
          <Search className="w-4 h-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Filter current view..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="w-full bg-transparent text-xs text-white placeholder-zinc-500 focus:outline-none"
          />
        </div>

        {/* Genre Selector */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#141824] border border-white/5">
          <Filter className="w-4 h-4 text-zinc-500" />
          <select
            value={selectedGenre}
            onChange={(e) => {
              setSelectedGenre(e.target.value);
              setPage(1);
            }}
            className="w-full bg-transparent text-xs text-white font-medium focus:outline-none"
          >
            <option value="" className="bg-[#141824]">All Genres</option>
            {genres.map((g) => (
              <option key={g.id} value={g.name} className="bg-[#141824]">
                {g.name}
              </option>
            ))}
          </select>
        </div>

        {/* Sort Selector */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#141824] border border-white/5">
          <ArrowUpDown className="w-4 h-4 text-zinc-500" />
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value);
              setPage(1);
            }}
            className="w-full bg-transparent text-xs text-white font-medium focus:outline-none"
          >
            <option value="popularity" className="bg-[#141824]">Most Popular</option>
            <option value="rating" className="bg-[#141824]">Highest Rated</option>
            <option value="recent" className="bg-[#141824]">Newest Release</option>
          </select>
        </div>
      </div>

      {/* Grid of items */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-6">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="aspect-[2/3] bg-white/5 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filteredItems.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 sm:gap-6">
          {filteredItems.map((item) => (
            <MediaCard
              key={`${item.media_type}-${item.id}`}
              item={item}
              onClick={onSelectMedia}
            />
          ))}
        </div>
      ) : (
        <div className="py-20 text-center text-zinc-500 bg-[#10141e] rounded-3xl border border-white/5">
          <p className="text-base font-semibold text-zinc-300">No titles match your active filters.</p>
          <p className="text-xs text-zinc-500 mt-1">Try resetting the genre or search term.</p>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex items-center justify-center gap-4 pt-8">
        <button
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1 || loading}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#141824] hover:bg-[#1d2334] disabled:opacity-30 text-xs font-semibold text-zinc-300 hover:text-white border border-white/5 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous</span>
        </button>

        <span className="text-xs font-semibold text-zinc-400">
          Page {page}
        </span>

        <button
          onClick={() => setPage(page + 1)}
          disabled={filteredItems.length < 12 || loading}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#141824] hover:bg-[#1d2334] disabled:opacity-30 text-xs font-semibold text-zinc-300 hover:text-white border border-white/5 transition-colors"
        >
          <span>Next</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

