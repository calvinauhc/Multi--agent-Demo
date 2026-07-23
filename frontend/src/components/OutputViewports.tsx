import React, { useState } from "react";
import { Copy, Check, Eye } from "lucide-react";

interface OutputViewportsProps {
  research: string;
}

export const OutputViewports: React.FC<OutputViewportsProps> = ({ research }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (research) {
      navigator.clipboard.writeText(research);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl flex flex-col h-[540px] shadow-xl overflow-hidden relative">
      {/* Glow background */}
      <div className="absolute top-0 left-0 w-32 h-32 bg-violet-600/5 rounded-full blur-2xl pointer-events-none" />

      {/* Header Panel */}
      <div className="flex border-b border-slate-800 bg-slate-950/60 p-4 items-center gap-2 flex-shrink-0">
        <div className="w-10 h-10 bg-blue-600/10 border border-blue-500/20 rounded-xl flex items-center justify-center text-lg">
          🔍
        </div>
        <div>
          <h3 className="text-sm font-semibold text-slate-100">Market Research Insights</h3>
          <p className="text-[10px] text-slate-500 uppercase tracking-wider">Comprehensive Housing Intel</p>
        </div>
        {research && (
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping ml-2" />
        )}
      </div>

      {/* Control bar */}
      <div className="bg-slate-950/20 border-b border-slate-850 px-4 py-2 flex justify-between items-center text-xs text-slate-400 flex-shrink-0">
        <div className="flex items-center gap-1">
          <Eye className="w-3.5 h-3.5" />
          <span>Research Viewport</span>
        </div>
        {research && (
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 bg-slate-950/80 hover:bg-slate-800 border border-slate-800 text-slate-300 px-3 py-1.5 rounded-lg active:scale-95 transition-all"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-green-400" />
                <span className="text-green-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-violet-400" />
                <span>Copy to Clipboard</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Viewport Content */}
      <div className="flex-1 overflow-y-auto p-6 bg-slate-950/40 relative">
        {research ? (
          <div className="prose prose-invert max-w-none text-xs text-slate-300 space-y-4 whitespace-pre-wrap leading-relaxed font-normal">
            <div className="space-y-3">
              {research.split("\n").map((line, idx) => {
                if (line.startsWith("### ")) {
                  return (
                    <h4 key={idx} className="text-slate-100 font-bold text-sm border-b border-slate-800/80 pb-1 mt-5 first:mt-0 uppercase tracking-wide">
                      {line.replace("### ", "")}
                    </h4>
                  );
                }
                if (line.startsWith("## ")) {
                  return (
                    <h3 key={idx} className="text-slate-100 font-extrabold text-base border-b border-slate-800 pb-1 mt-6 first:mt-0 uppercase tracking-wide">
                      {line.replace("## ", "")}
                    </h3>
                  );
                }
                if (line.startsWith("**") && line.endsWith("**")) {
                  return (
                    <p key={idx} className="font-bold text-slate-200 mt-2 text-xs">
                      {line.replace(/\*\*/g, "")}
                    </p>
                  );
                }
                if (line.startsWith("- ")) {
                  return (
                    <div key={idx} className="flex items-start gap-2 pl-2">
                      <span className="text-violet-400 mt-1 flex-shrink-0 text-[10px]">◆</span>
                      <span>{line.substring(2)}</span>
                    </div>
                  );
                }
                return <p key={idx} className="min-h-[0.5rem]">{line}</p>;
              })}
            </div>
          </div>
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-slate-950/10">
            <div className="w-12 h-12 rounded-full border border-slate-800 flex items-center justify-center text-lg text-slate-600 mb-3 bg-slate-950">
              🔍
            </div>
            <p className="text-sm font-medium text-slate-550 max-w-xs leading-relaxed">
              The Researcher's market summaries and transaction data records will appear here once the analysis completes.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
