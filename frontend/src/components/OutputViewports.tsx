import React, { useState } from "react";
import { FileText, Award, Send, Copy, Check, Eye } from "lucide-react";

interface OutputViewportsProps {
  research: string;
  analysis: string;
  post: string;
}

export const OutputViewports: React.FC<OutputViewportsProps> = ({
  research,
  analysis,
  post,
}) => {
  const [activeTab, setActiveTab] = useState<"research" | "analysis" | "post">("post");
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    // If we have a post, let's copy it to the clipboard
    const textToCopy = activeTab === "post" ? post : activeTab === "analysis" ? analysis : research;
    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const tabs = [
    {
      id: "post" as const,
      label: "Final IG Post",
      icon: Send,
      color: "text-violet-400 border-violet-500",
      activeBg: "bg-violet-600/10",
      content: post,
      placeholder: "The final Instagram post layout (caption, hashtags, and DALL-E visual prompts) will appear here.",
    },
    {
      id: "analysis" as const,
      label: "Content Strategy",
      icon: Award,
      color: "text-emerald-400 border-emerald-500",
      activeBg: "bg-emerald-600/10",
      content: analysis,
      placeholder: "The Analyst's strategic structure (user personas, slide storyboards, emotional hooks) will appear here.",
    },
    {
      id: "research" as const,
      label: "Market Research",
      icon: FileText,
      color: "text-blue-400 border-blue-500",
      activeBg: "bg-blue-600/10",
      content: research,
      placeholder: "The Researcher's market summaries and the Reviewer's compliance audits will appear here.",
    },
  ];

  const currentTab = tabs.find((t) => t.id === activeTab)!;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl flex flex-col h-[540px] shadow-xl overflow-hidden relative">
      {/* Glow background */}
      <div className="absolute top-0 left-0 w-32 h-32 bg-violet-600/5 rounded-full blur-2xl pointer-events-none" />

      {/* Tabs list */}
      <div className="flex border-b border-slate-800 bg-slate-950/60 p-2 gap-1.5 flex-shrink-0">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl text-xs font-semibold border transition-all ${
                isActive
                  ? `border-slate-800 text-slate-100 ${tab.activeBg}`
                  : "bg-transparent border-transparent text-slate-500 hover:text-slate-300"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.content && (
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping" />
              )}
            </button>
          );
        })}
      </div>

      {/* Control bar */}
      <div className="bg-slate-950/20 border-b border-slate-850 px-4 py-2 flex justify-between items-center text-xs text-slate-400 flex-shrink-0">
        <div className="flex items-center gap-1">
          <Eye className="w-3.5 h-3.5" />
          <span>Stage Output Viewport</span>
        </div>
        {currentTab.content && (
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
        {currentTab.content ? (
          <div className="prose prose-invert max-w-none text-xs text-slate-300 space-y-4 whitespace-pre-wrap leading-relaxed font-normal">
            {/* Direct formatted markdown rendering inside a simple, highly-legible block */}
            <div className="space-y-3">
              {currentTab.content.split("\n").map((line, idx) => {
                // Render custom simple markers to look like headings or checklists
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
              📊
            </div>
            <p className="text-sm font-medium text-slate-500 max-w-xs leading-relaxed">
              {currentTab.placeholder}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
