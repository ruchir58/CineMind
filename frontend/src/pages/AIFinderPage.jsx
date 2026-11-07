import React, { useState } from 'react';
import { Sparkles, Send, Brain, Bot, CornerDownLeft, RefreshCw, Compass, ArrowRight, Tag } from 'lucide-react';
import { generateAIRecommendations } from '../services/api';
import MediaCard from '../components/MediaCard';
import ExplanationBadge from '../components/ExplanationBadge';

const SAMPLE_PROMPTS = [
  "I want a psychological thriller with an unpredictable ending.",
  "Suggest a TV show similar to Dark and Severance.",
  "Recommend crime dramas released after 2015.",
  "I want a science-fiction movie with time travel, mystery and emotional depth.",
  "Suggest something dark, suspenseful and intellectually challenging.",
  "Find movies with mind-bending plots similar to Inception.",
  "Something like Dark but with less time travel."
];

export default function AIFinderPage({ onSelectMedia }) {
  const [prompt, setPrompt] = useState('');
  const [mediaType, setMediaType] = useState('all');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [extractedInfo, setExtractedInfo] = useState(null);
  const [submittedPrompt, setSubmittedPrompt] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

  const handleSubmit = async (promptText = prompt) => {
    const textToSubmit = (typeof promptText === 'string' ? promptText : prompt).trim();
    if (textToSubmit.length < 3) return;

    setLoading(true);
    setHasSearched(true);
    setSubmittedPrompt(textToSubmit);

    try {
      const res = await generateAIRecommendations({
        prompt: textToSubmit,
        media_type: mediaType,
        top_n: 10
      });

      setResults(res.recommendations || []);
      setExtractedInfo(res.extracted_preferences || null);
    } catch (err) {
      console.error('Error generating AI recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSelectSample = (sample) => {
    setPrompt(sample);
    handleSubmit(sample);
  };

  return (
    <div className="pt-24 sm:pt-28 pb-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
      {/* Page Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-950/80 to-purple-950/80 border border-indigo-500/30 text-indigo-300 text-xs font-semibold shadow-glow">
          <Brain className="w-3.5 h-3.5 text-indigo-400" />
          <span>Sentence Transformers • Semantic Embeddings</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          AI Movie Finder
        </h1>
        <p className="text-sm sm:text-base text-zinc-400 leading-relaxed">
          Describe the feeling, narrative twist, atmosphere, or reference titles you are looking for in natural human language.
        </p>
      </div>

      {/* Main Conversational Prompt Input Card */}
      <div className="bg-[#10141e] border border-indigo-500/20 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />

        {/* Media type toggle */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-zinc-400">
            <Bot className="w-4 h-4 text-indigo-400" />
            <span>Target Catalog:</span>
          </div>
          <div className="flex rounded-xl bg-[#141824] p-1 border border-white/5">
            {[
              { id: 'all', label: 'All Content' },
              { id: 'movie', label: 'Movies Only' },
              { id: 'tv', label: 'TV Shows Only' },
            ].map((type) => (
              <button
                key={type.id}
                onClick={() => setMediaType(type.id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
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

        {/* Prompt Input Box */}
        <div className="relative">
          <textarea
            rows="3"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe the kind of movie or TV show you're in the mood for... (e.g. 'I want a mind-bending sci-fi with time travel and emotional depth')"
            className="w-full p-4 sm:p-5 rounded-2xl bg-[#141824] border border-white/10 text-white placeholder-zinc-500 text-sm sm:text-base focus:outline-none focus:border-indigo-500 transition-colors resize-none leading-relaxed"
          />

          <div className="flex items-center justify-between pt-3">
            <span className="hidden sm:inline text-xs text-zinc-500 flex items-center gap-1">
              Press <kbd className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] text-zinc-400">Enter ↵</kbd> to submit
            </span>

            <button
              onClick={() => handleSubmit()}
              disabled={loading || prompt.trim().length < 3}
              className="ml-auto flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-600 disabled:opacity-40 text-white font-bold text-sm shadow-glow transition-all"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Analyzing Semantics...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Discover Titles</span>
                  <CornerDownLeft className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Suggested Example Prompts */}
        <div className="space-y-2.5 pt-2">
          <span className="text-xs font-semibold text-zinc-400">
            Suggested Example Prompts:
          </span>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_PROMPTS.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectSample(sample)}
                className="text-left px-3.5 py-2 rounded-xl text-xs font-medium bg-[#141824] hover:bg-[#1d2334] text-zinc-300 hover:text-white border border-white/5 hover:border-indigo-500/30 transition-all flex items-center gap-2"
              >
                <span>{sample}</span>
                <ArrowRight className="w-3 h-3 text-indigo-400 opacity-60" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Extracted Intent Diagnostic Banner */}
      {extractedInfo && hasSearched && (
        <div className="p-4 rounded-2xl bg-[#11151e] border border-white/5 flex flex-wrap items-center gap-3 text-xs text-zinc-400">
          <span className="font-bold text-zinc-300">Extracted Preferences:</span>
          {extractedInfo.media_type && extractedInfo.media_type !== 'all' && (
            <span className="px-2.5 py-1 rounded-full bg-white/5 text-zinc-300">
              Format: {extractedInfo.media_type.toUpperCase()}
            </span>
          )}
          {extractedInfo.detected_genres && extractedInfo.detected_genres.length > 0 && (
            <span className="px-2.5 py-1 rounded-full bg-indigo-950/40 text-indigo-300 border border-indigo-500/20">
              Genres: {extractedInfo.detected_genres.join(', ').toUpperCase()}
            </span>
          )}
          {extractedInfo.detected_moods && extractedInfo.detected_moods.length > 0 && (
            <span className="px-2.5 py-1 rounded-full bg-purple-950/40 text-purple-300 border border-purple-500/20">
              Mood: {extractedInfo.detected_moods.join(', ')}
            </span>
          )}
          {extractedInfo.reference_titles && extractedInfo.reference_titles.length > 0 && (
            <span className="px-2.5 py-1 rounded-full bg-sky-950/40 text-sky-300 border border-sky-500/20">
              Reference: {extractedInfo.reference_titles.join(', ')}
            </span>
          )}
          {extractedInfo.negative_features && extractedInfo.negative_features.length > 0 && (
            <span className="px-2.5 py-1 rounded-full bg-rose-950/40 text-rose-300 border border-rose-500/20">
              Excluded: {extractedInfo.negative_features.join(', ')}
            </span>
          )}
          {extractedInfo.min_year && (
            <span className="px-2.5 py-1 rounded-full bg-white/5 text-zinc-300">
              Year: &gt; {extractedInfo.min_year}
            </span>
          )}
        </div>
      )}

      {/* Results View */}
      {hasSearched && (
        <div className="space-y-8">
          <div className="flex items-center justify-between border-b border-white/5 pb-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                <span>AI Recommended Titles ({results.length})</span>
              </h2>
              {submittedPrompt && (
                <p className="text-xs text-zinc-400 mt-1 italic">
                  Prompt: "{submittedPrompt}"
                </p>
              )}
            </div>
          </div>

          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-4 text-center">
              <div className="w-12 h-12 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm font-semibold text-zinc-300">Scanning semantic embedding manifold...</p>
              <p className="text-xs text-zinc-500">Matching narrative themes, plot characteristics and tone</p>
            </div>
          ) : results.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {results.map((rec) => (
                <div
                  key={`${rec.media.media_type}-${rec.media.id}`}
                  className="bg-[#10141d] border border-white/5 rounded-3xl p-5 flex flex-col sm:flex-row gap-5 hover:border-indigo-500/30 transition-all shadow-lg"
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
                      className="w-full py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-zinc-300 hover:text-white transition-colors"
                    >
                      View Synopsis & Cast
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center text-zinc-500 bg-[#10141d] rounded-3xl border border-white/5">
              <p className="text-base font-semibold text-zinc-300">No matching titles found for this description.</p>
              <p className="text-xs text-zinc-500 mt-1">Try rewording your prompt or removing restrictive criteria.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

