import React from 'react';
import { Sparkles, CheckCircle2, Tag, Compass } from 'lucide-react';

export default function ExplanationBadge({ explanation, title }) {
  if (!explanation) return null;

  const { matched_features = [], summary = '', genre_alignment, mood_alignment } = explanation;

  return (
    <div className="bg-[#121620] border border-indigo-500/20 rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-indigo-400" />
        <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
          Why We Recommended This
        </h4>
      </div>

      {summary && (
        <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed font-normal">
          {summary}
        </p>
      )}

      {matched_features.length > 0 && (
        <ul className="space-y-1.5 pt-1">
          {matched_features.map((feature, idx) => (
            <li key={idx} className="flex items-start gap-2 text-xs text-zinc-400">
              <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      )}

      {(genre_alignment || mood_alignment) && (
        <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-white/5">
          {genre_alignment && (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-white/5 text-zinc-300">
              <Tag className="w-2.5 h-2.5 text-zinc-400" />
              {genre_alignment}
            </span>
          )}
          {mood_alignment && (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-950/40 text-indigo-300 border border-indigo-500/20">
              <Compass className="w-2.5 h-2.5 text-indigo-400" />
              {mood_alignment}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

