import React from "react";
import { Search, Settings, Sparkles, AlertCircle, ArrowRight } from "lucide-react";

interface InputPanelProps {
  query: string;
  setQuery: (val: string) => void;
  tone: string;
  setTone: (val: string) => void;
  provider: string;
  isLoading: boolean;
  onGenerate: () => void;
  onOpenSettings: () => void;
}

export const InputPanel: React.FC<InputPanelProps> = ({
  query,
  setQuery,
  tone,
  setTone,
  provider,
  isLoading,
  onGenerate,
  onOpenSettings,
}) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !isLoading) {
      e.preventDefault();
      onGenerate();
    }
  };

  const sampleQueries = [
    "Suburban condo yields vs city center luxury",
    "Eco-friendly smart homes in green townships",
    "Rise of co-living spaces for digital nomads",
    "Commercial real estate trends in major cities",
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
      {/* Glow background */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-violet-600/5 rounded-full blur-2xl pointer-events-none" />

      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-violet-400" /> System Inputs
        </h3>
        <button
          onClick={onOpenSettings}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800 rounded-lg px-2.5 py-1.5 transition-all"
        >
          <Settings className="w-3.5 h-3.5" />
          <span>Config ({provider === "mock" ? "Simulation" : provider})</span>
        </button>
      </div>

      <div className="space-y-4">
        {/* Main Query input */}
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-2">
            WHAT SHOULD THE AGENTS RESEARCH AND CAPTURE?
          </label>
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              rows={3}
              placeholder="e.g. Research top suburban real estate yield trends and write a copy detailing capital appreciation versus city core properties..."
              className="w-full bg-slate-950 border border-slate-800 focus:border-violet-500 rounded-xl pl-4 pr-10 py-3 text-sm text-slate-100 placeholder:text-slate-600 outline-none transition-all disabled:opacity-50 resize-none"
            />
            <div className="absolute right-3 bottom-3 text-slate-600">
              <Search className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* Tone Selection */}
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-2">
            INSTAGRAM POST CAPTION TONE
          </label>
          <div className="grid grid-cols-4 gap-2">
            {["professional", "enthusiastic", "bold", "analytical"].map((t) => (
              <button
                key={t}
                type="button"
                disabled={isLoading}
                onClick={() => setTone(t)}
                className={`py-2 px-1 rounded-lg text-xs font-medium border capitalize transition-all ${
                  tone === t
                    ? "bg-violet-600/10 border-violet-500 text-violet-300"
                    : "bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700 hover:text-slate-300"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={onGenerate}
          disabled={isLoading || !query.trim()}
          className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-600 text-white rounded-xl py-3 text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-violet-900/10 hover:shadow-violet-900/20 active:scale-[0.99] transition-all"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Orchestrating Agents...</span>
            </>
          ) : (
            <>
              <span>Run Multi-Agent Cycle</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>

        {/* Clickable Sample Queries */}
        {!isLoading && (
          <div className="pt-2">
            <span className="block text-[11px] font-semibold text-slate-500 mb-1.5 uppercase">
              Or choose a sample topic:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {sampleQueries.map((sample) => (
                <button
                  key={sample}
                  type="button"
                  onClick={() => setQuery(sample)}
                  className="text-xs text-slate-400 bg-slate-950 border border-slate-800/80 hover:border-slate-700 rounded-md px-2.5 py-1 transition-all"
                >
                  {sample}
                </button>
              ))}
            </div>
          </div>
        )}

        {provider !== "mock" && (
          <div className="bg-slate-950 border border-slate-800/60 rounded-xl p-3 flex gap-2 items-start text-xs text-slate-400">
            <AlertCircle className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              Running with real LLMs. Ensure your <strong>{provider}</strong> API key has enough quota. The research loop will make 5 API calls in sequence.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
