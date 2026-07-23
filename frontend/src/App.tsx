import { useState } from "react";
import { SettingsModal } from "./components/SettingsModal";
import { InputPanel } from "./components/InputPanel";
import { AgentLogStream } from "./components/AgentLogStream";
import type { AgentLog } from "./components/AgentLogStream";
import { OutputViewports } from "./components/OutputViewports";
import { Building2, Layers, ShieldAlert } from "lucide-react";

function App() {
  // Read local settings on startup
  const [provider, setProvider] = useState<string>(() => {
    return localStorage.getItem("llm_provider") || "mock";
  });
  const [apiKey, setApiKey] = useState<string>(() => {
    return localStorage.getItem("llm_api_key") || "";
  });

  const [query, setQuery] = useState("");
  const [tone, setTone] = useState("professional");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Agent Progress States
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [activeAgent, setActiveAgent] = useState("");
  const [activeStatus, setActiveStatus] = useState("");
  const [progress, setProgress] = useState(0);

  // Final Output States
  const [research, setResearch] = useState("");
  const [analysis, setAnalysis] = useState("");
  const [post, setPost] = useState("");

  const handleGenerate = () => {
    if (!query.trim()) return;

    // Reset old outputs
    setIsLoading(true);
    setErrorMsg(null);
    setLogs([]);
    setActiveAgent("");
    setActiveStatus("");
    setProgress(0);
    setResearch("");
    setAnalysis("");
    setPost("");

    // Build Server Sent Events connection url
    let baseUrl = "http://localhost:8000/api/generate";
    if (window.location.hostname === "127.0.0.1") {
      baseUrl = "http://127.0.0.1:8000/api/generate";
    } else if (window.location.hostname !== "localhost") {
      // Robust proxy port replacement (e.g., 5173 -> 8000)
      baseUrl = window.location.origin
        .replace("5173", "8000")
        .replace(":5173", ":8000") + "/api/generate";
    }
    const params = new URLSearchParams({
      query: query.trim(),
      tone: tone,
      provider: provider,
    });

    if (provider !== "mock" && apiKey) {
      params.append("api_key", apiKey);
    }

    const eventSourceUrl = `${baseUrl}?${params.toString()}`;

    // Establish SSE Connection
    // Support authenticated Coder/VS Code proxies by passing credentials (cookies)
    const eventSource = new EventSource(eventSourceUrl, {
      withCredentials: true,
    });

    // EventSource error handler
    eventSource.onerror = (e) => {
      console.error("SSE connection error:", e);
      setErrorMsg(
        provider !== "mock" && !apiKey
          ? "API Key is required. Please open settings and supply a valid API key."
          : "Could not establish real-time connection to backend. Make sure the FastAPI server is running on port 8000."
      );
      setIsLoading(false);
      eventSource.close();
    };

    // Listen to custom agent log updates
    eventSource.addEventListener("log", (event) => {
      try {
        const payload = JSON.parse(event.data);
        setLogs((prev) => [...prev, payload]);
      } catch (err) {
        console.error("Error parsing log payload:", err);
      }
    });

    // Listen to agent status updates
    eventSource.addEventListener("status", (event) => {
      try {
        const payload = JSON.parse(event.data);
        setActiveAgent(payload.agent);
        setActiveStatus(payload.status);
        setProgress(payload.progress);
      } catch (err) {
        console.error("Error parsing status payload:", err);
      }
    });

    // Listen to agent stage completions
    eventSource.addEventListener("result", (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.stage === "research") {
          setResearch(payload.data);
        } else if (payload.stage === "analysis") {
          setAnalysis(payload.data);
        } else if (payload.stage === "writer") {
          setPost(payload.data);
        }
      } catch (err) {
        console.error("Error parsing result payload:", err);
      }
    });

    // Listen to final complete event
    eventSource.addEventListener("done", () => {
      try {
        setActiveAgent("Done");
        setActiveStatus("complete");
        setProgress(100);
        setIsLoading(false);
        eventSource.close();
      } catch (err) {
        console.error("Error handling done event:", err);
        setIsLoading(false);
        eventSource.close();
      }
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
      {/* Settings Modal component */}
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        provider={provider}
        setProvider={setProvider}
        apiKey={apiKey}
        setApiKey={setApiKey}
      />

      {/* Modern Navigation Header */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md px-6 py-4 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-violet-900/30">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-white m-0 p-0 flex items-center gap-2">
                Real Estate AI Writer <span className="text-[10px] bg-violet-600/30 text-violet-300 font-semibold px-2 py-0.5 rounded-full border border-violet-500/20">v2.0</span>
              </h1>
              <p className="text-[11px] text-slate-400 mt-0.5 font-medium uppercase tracking-wider">Multi-Agent Research & Social Composer</p>
            </div>
          </div>

          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2 text-xs bg-slate-900/60 border border-slate-800/80 rounded-xl p-2 px-3">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-slate-400 font-medium">Mode:</span>
              <span className="text-slate-200 font-semibold uppercase">
                {provider === "mock" ? "Simulation (No Keys)" : `${provider} (Real LLM)`}
              </span>
            </div>

            <button
              onClick={() => setSettingsOpen(true)}
              className="text-xs bg-violet-600 hover:bg-violet-500 text-white font-semibold rounded-xl px-4 py-2.5 shadow-lg shadow-violet-900/20 active:scale-95 transition-all"
            >
              Configure Keys
            </button>
          </div>
        </div>
      </header>

      {/* Main Grid Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left Control Panel (Span 4) */}
        <div className="lg:col-span-4 space-y-6">
          <InputPanel
            query={query}
            setQuery={setQuery}
            tone={tone}
            setTone={setTone}
            provider={provider}
            isLoading={isLoading}
            onGenerate={handleGenerate}
            onOpenSettings={() => setSettingsOpen(true)}
          />

          {/* Quick Informational Guide */}
          <div className="bg-slate-900/40 border border-slate-900 rounded-xl p-4 space-y-3">
            <h4 className="text-xs font-bold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-violet-400" /> Collaboration Scheme
            </h4>
            <div className="space-y-2.5 text-xs text-slate-400">
              <div className="flex gap-2.5 items-start">
                <span className="text-base leading-none">🔍</span>
                <p>
                  <strong>Researcher:</strong> Analyzes raw market indices (transaction values, yields, demographics) matching your topic.
                </p>
              </div>
              <div className="flex gap-2.5 items-start">
                <span className="text-base leading-none">🧐</span>
                <p>
                  <strong>Reviewer:</strong> Audits metrics for accuracy and appends compliance disclaimers. Refines research reports.
                </p>
              </div>
              <div className="flex gap-2.5 items-start">
                <span className="text-base leading-none">📊</span>
                <p>
                  <strong>Analyst:</strong> Strategizes visual storyboards, emotional triggers, and audience alignment.
                </p>
              </div>
              <div className="flex gap-2.5 items-start">
                <span className="text-base leading-none">✍️</span>
                <p>
                  <strong>Writer:</strong> Crafts final viral captions, hook structures, hashtag sets, and realistic image prompt guides.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Dashboard Workspace (Span 8) */}
        <div className="lg:col-span-8 flex flex-col gap-6">

          {/* Error Banner */}
          {errorMsg && (
            <div className="bg-red-600/10 border border-red-500/30 rounded-xl p-4 flex gap-3 items-center text-xs text-red-300 animate-fadeIn">
              <ShieldAlert className="w-5 h-5 text-red-400 flex-shrink-0" />
              <div className="flex-1">
                <span className="font-semibold block">Execution Interrupted</span>
                <p className="mt-0.5 leading-relaxed">{errorMsg}</p>
              </div>
            </div>
          )}

          {/* Dual Panel (Feed and Viewports) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
            <AgentLogStream
              logs={logs}
              activeAgent={activeAgent}
              activeStatus={activeStatus}
              progress={progress}
            />

            <OutputViewports
              research={research}
              analysis={analysis}
              post={post}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/40 p-4 text-center text-xs text-slate-500 mt-auto">
        <p>© 2026 Property Agentic Social Platform. Powered by Server-Sent Events & FastAPI.</p>
      </footer>
    </div>
  );
}

export default App;
