import React, { useState, useEffect } from 'react';
import { X, Star, Clock, Calendar, Users, Clapperboard, Globe, Sparkles, Tv, Film, Play, Bookmark, BookmarkCheck } from 'lucide-react';
import { getBackdropUrl, getPosterUrl, fetchMovieById, fetchTvById, fetchSimilar } from '../services/api';

export default function MediaDetailsModal({ media, onClose, onSelectMedia }) {
  const [details, setDetails] = useState(media);
  const [similarItems, setSimilarItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isPlayingTrailer, setIsPlayingTrailer] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    if (!media) return;
    setDetails(media);
    setIsPlayingTrailer(false);

    // Check if item is saved in localStorage
    try {
      const saved = JSON.parse(localStorage.getItem('cinemind_watchlist') || '[]');
      setIsSaved(saved.some((item) => item.id === media.id && item.media_type === media.media_type));
    } catch (e) {
      console.warn('localStorage error:', e);
    }

    const loadExtraDetails = async () => {
      setLoading(true);
      try {
        let fullData = null;
        if (media.media_type === 'tv') {
          fullData = await fetchTvById(media.id);
        } else {
          fullData = await fetchMovieById(media.id);
        }
        if (fullData) {
          setDetails(fullData);
        }

        const sim = await fetchSimilar(media.media_type || 'movie', media.id);
        if (Array.isArray(sim)) {
          setSimilarItems(sim.slice(0, 8));
        }
      } catch (err) {
        console.error('Error fetching extended media details:', err);
      } finally {
        setLoading(false);
      }
    };

    loadExtraDetails();
  }, [media]);

  // Toggle watchlist in localStorage
  const toggleWatchlist = () => {
    try {
      const saved = JSON.parse(localStorage.getItem('cinemind_watchlist') || '[]');
      const exists = saved.some((item) => item.id === details.id && item.media_type === details.media_type);

      let updated;
      if (exists) {
        updated = saved.filter((item) => !(item.id === details.id && item.media_type === details.media_type));
        setIsSaved(false);
      } else {
        updated = [details, ...saved];
        setIsSaved(true);
      }
      localStorage.setItem('cinemind_watchlist', JSON.stringify(updated));
      window.dispatchEvent(new Event('watchlistUpdated'));
    } catch (e) {
      console.error('Watchlist save error:', e);
    }
  };

  // Handle ESC key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!media) return null;

  const releaseDate = details.release_date || details.first_air_date || '';
  const releaseYear = releaseDate ? releaseDate.substring(0, 4) : 'N/A';

  const genres = Array.isArray(details.genres)
    ? details.genres
    : typeof details.genres === 'string'
    ? details.genres.split(',').map((g) => g.trim())
    : [];

  const castList = Array.isArray(details.cast)
    ? details.cast
    : typeof details.cast === 'string'
    ? details.cast.split(',').map((c) => c.trim())
    : [];

  const creatorsOrDirector = details.media_type === 'tv'
    ? details.creators && details.creators.length > 0 ? details.creators.join(', ') : 'Various Creators'
    : details.director || 'N/A';

  const trailerKey = details.trailer_key;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-4xl bg-[#0f131c] border border-white/10 rounded-2xl sm:rounded-3xl shadow-2xl overflow-hidden my-auto max-h-[92vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2.5 rounded-full bg-black/60 hover:bg-black/90 text-zinc-300 hover:text-white border border-white/10 transition-colors backdrop-blur-md"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Scrollable Body */}
        <div className="overflow-y-auto flex-1">
          {/* Header Backdrop / Trailer Player */}
          <div className="relative w-full h-64 sm:h-96 bg-[#161a24] overflow-hidden">
            {isPlayingTrailer && trailerKey ? (
              <div className="w-full h-full relative bg-black">
                <iframe
                  src={`https://www.youtube-nocookie.com/embed/${trailerKey}?autoplay=1&rel=0`}
                  title={`${details.title} Trailer`}
                  className="w-full h-full border-0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
                <button
                  onClick={() => setIsPlayingTrailer(false)}
                  className="absolute top-4 left-4 z-10 px-3 py-1.5 rounded-xl bg-black/70 hover:bg-black/90 text-xs font-semibold text-white border border-white/10 flex items-center gap-1.5 backdrop-blur-md"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Close Player</span>
                </button>
              </div>
            ) : (
              <>
                <img
                  src={getBackdropUrl(details.backdrop_path)}
                  alt={details.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0f131c] via-[#0f131c]/60 to-transparent" />
                
                {/* Title & Quick badges overlay */}
                <div className="absolute bottom-4 left-6 right-6 flex items-end gap-6">
                  <div className="hidden sm:block w-32 aspect-[2/3] rounded-xl overflow-hidden shadow-2xl border-2 border-white/10 bg-[#181d28] shrink-0 -mb-8 z-10">
                    <img
                      src={getPosterUrl(details.poster_path)}
                      alt={details.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-600/80 text-white border border-indigo-400/30">
                        {details.media_type === 'tv' ? 'TV Series' : 'Movie'}
                      </span>
                      {details.vote_average > 0 && (
                        <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                          {details.vote_average.toFixed(1)} / 10
                        </span>
                      )}
                      {releaseYear !== 'N/A' && (
                        <span className="text-xs text-zinc-400 font-medium">
                          {releaseYear}
                        </span>
                      )}
                    </div>
                    <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight drop-shadow-md">
                      {details.title}
                    </h2>
                    {details.original_title && details.original_title !== details.title && (
                      <p className="text-xs text-zinc-400 italic mt-0.5">
                        Original: {details.original_title}
                      </p>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Action Bar: Trailer + Watchlist */}
          <div className="px-6 sm:px-8 pt-4 pb-2 flex items-center gap-3 flex-wrap">
            {trailerKey ? (
              <button
                onClick={() => setIsPlayingTrailer(true)}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-glow transition-all"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Watch Official Trailer</span>
              </button>
            ) : (
              <a
                href={`https://www.youtube.com/results?search_query=${encodeURIComponent(details.title + ' ' + (details.media_type === 'tv' ? 'trailer series' : 'trailer movie'))}`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#1a202c] hover:bg-[#252e3e] text-zinc-200 hover:text-white text-xs font-semibold border border-white/5 transition-all"
              >
                <Play className="w-3.5 h-3.5 text-indigo-400" />
                <span>Search Trailer on YouTube</span>
              </a>
            )}

            <button
              onClick={toggleWatchlist}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold border transition-all ${
                isSaved
                  ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
                  : 'bg-[#141824] hover:bg-[#1c2232] border-white/10 text-zinc-300 hover:text-white'
              }`}
            >
              {isSaved ? (
                <>
                  <BookmarkCheck className="w-4 h-4 text-emerald-400" />
                  <span>Saved to Watchlist</span>
                </>
              ) : (
                <>
                  <Bookmark className="w-4 h-4 text-zinc-400" />
                  <span>Add to Watchlist</span>
                </>
              )}
            </button>
          </div>

          {/* Details Content */}
          <div className="p-6 sm:p-8 space-y-8">
            {/* Metadata Bar */}
            <div className="flex flex-wrap items-center gap-4 text-xs sm:text-sm text-zinc-400 border-b border-white/5 pb-4">
              {details.runtime ? (
                <div className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-indigo-400" />
                  <span>{details.runtime} mins</span>
                </div>
              ) : details.number_of_seasons ? (
                <div className="flex items-center gap-1.5">
                  <Tv className="w-4 h-4 text-indigo-400" />
                  <span>{details.number_of_seasons} Season{details.number_of_seasons > 1 ? 's' : ''} ({details.number_of_episodes || 0} Episodes)</span>
                </div>
              ) : null}

              {releaseDate && (
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-indigo-400" />
                  <span>Released: {releaseDate}</span>
                </div>
              )}

              {details.original_language && (
                <div className="flex items-center gap-1.5 uppercase">
                  <Globe className="w-4 h-4 text-indigo-400" />
                  <span>Language: {details.original_language}</span>
                </div>
              )}

              {details.status && (
                <div className="px-2 py-0.5 rounded text-xs bg-white/5 text-zinc-300">
                  Status: {details.status}
                </div>
              )}
            </div>

            {/* Genres */}
            {genres.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {genres.map((genre, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 rounded-full text-xs font-semibold bg-[#181d28] hover:bg-[#222938] text-zinc-200 border border-white/5 transition-colors"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            )}

            {/* Overview */}
            <div className="space-y-2">
              <h3 className="text-sm uppercase font-bold tracking-wider text-zinc-400">
                Storyline
              </h3>
              <p className="text-sm sm:text-base text-zinc-300 leading-relaxed">
                {details.overview || 'No storyline summary available.'}
              </p>
            </div>

            {/* Credits Section */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-[#131722]/60 p-5 rounded-2xl border border-white/5">
              <div>
                <h4 className="text-xs uppercase font-bold tracking-wider text-zinc-400 flex items-center gap-1.5 mb-2">
                  <Clapperboard className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{details.media_type === 'tv' ? 'Creators' : 'Director'}</span>
                </h4>
                <p className="text-sm font-semibold text-white">
                  {creatorsOrDirector}
                </p>
              </div>

              {castList.length > 0 && (
                <div>
                  <h4 className="text-xs uppercase font-bold tracking-wider text-zinc-400 flex items-center gap-1.5 mb-2">
                    <Users className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Key Cast</span>
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {castList.slice(0, 6).map((actor, idx) => (
                      <span key={idx} className="text-xs text-zinc-300 px-2 py-0.5 rounded bg-white/5">
                        {actor}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Similar Titles */}
            {similarItems.length > 0 && (
              <div className="space-y-4 pt-4 border-t border-white/5">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-base font-bold text-white">
                    Similar {details.media_type === 'tv' ? 'TV Shows' : 'Movies'} You May Like
                  </h3>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {similarItems.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => onSelectMedia(item)}
                      className="group p-2 rounded-xl bg-[#141824] hover:bg-[#1d2334] cursor-pointer transition-colors border border-white/5"
                    >
                      <div className="aspect-[2/3] rounded-lg overflow-hidden bg-[#181d28] mb-2">
                        <img
                          src={getPosterUrl(item.poster_path, 'w200')}
                          alt={item.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      </div>
                      <h4 className="text-xs font-semibold text-white truncate group-hover:text-indigo-400">
                        {item.title}
                      </h4>
                      <p className="text-[10px] text-zinc-500">
                        {item.release_date ? item.release_date.substring(0, 4) : ''}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

