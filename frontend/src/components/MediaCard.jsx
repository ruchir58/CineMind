import React from 'react';
import { Star, Film, Tv, Sparkles } from 'lucide-react';
import { getPosterUrl } from '../services/api';

export default function MediaCard({ item, similarityScore, onClick, showExplanationBadge = false, explanation = null }) {
  const media = item.media || item;
  const score = similarityScore || (item.similarity_score ? item.similarity_score : null);

  const releaseYear = media.release_date
    ? media.release_date.substring(0, 4)
    : media.first_air_date
    ? media.first_air_date.substring(0, 4)
    : '';

  const genresList = Array.isArray(media.genres)
    ? media.genres.slice(0, 2).join(' • ')
    : typeof media.genres === 'string'
    ? media.genres.split(',').slice(0, 2).join(' • ')
    : '';

  return (
    <div
      onClick={() => onClick && onClick(media)}
      className="group relative flex flex-col bg-[#11151e] border border-white/5 rounded-2xl overflow-hidden hover:border-indigo-500/40 hover:shadow-card hover:-translate-y-1.5 transition-all duration-300 cursor-pointer"
    >
      {/* Poster Image Container */}
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-[#181d28]">
        <img
          src={getPosterUrl(media.poster_path)}
          alt={media.title}
          loading="lazy"
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />

        {/* Gradient dark overlay on bottom of poster */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#11151e] via-transparent to-black/30 pointer-events-none" />

        {/* Media type badge */}
        <div className="absolute top-2.5 left-2.5 flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-black/60 backdrop-blur-md text-zinc-300 border border-white/10">
          {media.media_type === 'tv' ? (
            <>
              <Tv className="w-2.5 h-2.5 text-sky-400" />
              <span>TV Series</span>
            </>
          ) : (
            <>
              <Film className="w-2.5 h-2.5 text-indigo-400" />
              <span>Movie</span>
            </>
          )}
        </div>

        {/* Rating pill */}
        {media.vote_average > 0 && (
          <div className="absolute top-2.5 right-2.5 flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-black/60 backdrop-blur-md text-amber-300 border border-amber-400/20">
            <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
            <span>{media.vote_average.toFixed(1)}</span>
          </div>
        )}

        {/* Similarity Score Badge (if in recommendation mode) */}
        {score !== null && score !== undefined && (
          <div className="absolute bottom-2.5 right-2.5 flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-950/85 backdrop-blur-md text-indigo-300 border border-indigo-500/30 shadow-glow">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            <span>{Math.round(score * 100)}% Match</span>
          </div>
        )}
      </div>

      {/* Info Content */}
      <div className="p-4 flex flex-col flex-1 justify-between gap-2">
        <div>
          <h3 className="text-sm sm:text-base font-semibold text-white group-hover:text-indigo-400 transition-colors line-clamp-1">
            {media.title}
          </h3>
          <div className="flex items-center gap-2 mt-1 text-xs text-zinc-400">
            {releaseYear && <span>{releaseYear}</span>}
            {releaseYear && genresList && <span>•</span>}
            {genresList && <span className="line-clamp-1">{genresList}</span>}
          </div>
        </div>

        {/* Explanation snippet if present */}
        {showExplanationBadge && explanation && explanation.matched_features && explanation.matched_features.length > 0 && (
          <div className="mt-2 pt-2 border-t border-white/5 text-[11px] text-zinc-400 space-y-1">
            <p className="line-clamp-2 text-zinc-300 font-medium">
              💡 {explanation.matched_features[0]}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

