import React, { useEffect, useRef } from "react";
import { MessageSquare, RefreshCw, CheckCircle2 } from "lucide-react";

export interface AgentLog {
  agent: string;
  action: string;
  message: string;
}

interface AgentLogStreamProps {
  logs: AgentLog[];
  activeAgent: string;
  activeStatus: string;
  progress: number;
}

export const AgentLogStream: React.FC<AgentLogStreamProps> = ({
  logs,
  activeAgent,
  activeStatus,
  progress,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new logs arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, activeAgent, activeStatus]);

  // Map agents to avatars, icons, and colors
  const getAgentConfig = (agent: string) => {
    const name = agent.toLowerCase();
    if (name.includes("researcher")) {
      return {
        avatar: "🔍",
        bgColor: "bg-blue-600/10 border-blue-500/30",
        textColor: "text-blue-400",
        badge: "bg-blue-500/20 text-blue-300",
        title: "RESEARCHER"
      };
    }
    return {
      avatar: "🤖",
      bgColor: "bg-slate-800 border-slate-700",
      textColor: "text-slate-300",
      badge: "bg-slate-700 text-slate-300",
      title: "SYSTEM"
    };
  };

  const activeAgentConfig = getAgentConfig(activeAgent);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col h-[540px] shadow-xl relative overflow-hidden">
      {/* Glow background */}
      <div className="absolute bottom-0 right-0 w-32 h-32 bg-indigo-600/5 rounded-full blur-2xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center gap-2">
          <div className="relative">
            <MessageSquare className="w-5 h-5 text-violet-400" />
            {activeAgent && activeAgent !== "Done" && (
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-green-500 rounded-full animate-ping" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Agent Collaboration Feed</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Event Stream (SSE)</p>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-xs font-semibold text-slate-300">{progress}%</span>
          </div>
          <div className="w-24 bg-slate-950 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-violet-500 to-indigo-500 h-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Active agent banner if busy */}
      {activeAgent && activeAgent !== "Done" && (
        <div className={`mb-4 p-3 rounded-xl border flex items-center justify-between animate-pulse-slow ${activeAgentConfig.bgColor}`}>
          <div className="flex items-center gap-3">
            <span className="text-2xl">{activeAgentConfig.avatar}</span>
            <div>
              <span className="text-[10px] font-bold tracking-wider uppercase opacity-80 block text-slate-400">
                CURRENT ACTIVE AGENT
              </span>
              <span className={`text-sm font-bold ${activeAgentConfig.textColor}`}>
                {activeAgentConfig.title}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 bg-slate-950/60 border border-slate-800/40 rounded-lg px-3 py-1 text-xs text-slate-300 capitalize">
            <RefreshCw className="w-3.5 h-3.5 text-violet-400 animate-spin" />
            <span>{activeStatus}</span>
          </div>
        </div>
      )}

      {/* Empty State */}
      {logs.length === 0 && !activeAgent && (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-6">
          <div className="w-12 h-12 rounded-2xl bg-slate-950 border border-slate-800/80 flex items-center justify-center text-slate-600 mb-3">
            🤖
          </div>
          <p className="text-sm font-medium text-slate-400">Waiting for agent activation...</p>
          <p className="text-xs text-slate-600 mt-1 max-w-[240px]">
            Input a property query on the left to start the multi-agent orchestration.
          </p>
        </div>
      )}

      {/* Logs Scroll container */}
      <div ref={containerRef} className="flex-1 overflow-y-auto space-y-3.5 pr-1">
        {logs.map((log, index) => {
          const config = getAgentConfig(log.agent);
          return (
            <div
              key={index}
              className={`p-3.5 rounded-xl border bg-slate-950/40 hover:bg-slate-950/80 transition-all flex items-start gap-3.5 animate-fadeIn border-slate-800/60`}
            >
              {/* Avatar Icon */}
              <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-lg flex-shrink-0 shadow-inner">
                {config.avatar}
              </div>

              {/* Log Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1 gap-2 flex-wrap">
                  <span className={`text-xs font-bold tracking-wide uppercase ${config.textColor}`}>
                    {config.title}
                  </span>
                  <span className={`text-[9px] font-semibold px-2 py-0.5 rounded-md ${config.badge}`}>
                    {log.action}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-normal break-words">
                  {log.message}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Completion Alert */}
      {activeAgent === "Done" && (
        <div className="mt-4 p-3 bg-emerald-600/10 border border-emerald-500/30 rounded-xl flex items-center gap-2.5 animate-bounce-slow text-xs text-emerald-300 font-medium">
          <CheckCircle2 className="w-4.5 h-4.5 text-emerald-400" />
          <span>Research complete! Browse findings in the viewport.</span>
        </div>
      )}
    </div>
  );
};
