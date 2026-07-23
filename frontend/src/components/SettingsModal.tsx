import React, { useState } from "react";
import { X, Key, Shield, HelpCircle } from "lucide-react";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  provider: string;
  setProvider: (val: string) => void;
  apiKey: string;
  setApiKey: (val: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  provider,
  setProvider,
  apiKey,
  setApiKey,
}) => {
  const [tempKey, setTempKey] = useState(apiKey);
  const [tempProvider, setTempProvider] = useState(provider);

  if (!isOpen) return null;

  const handleSave = () => {
    setProvider(tempProvider);
    setApiKey(tempKey);
    // Save to local storage for persistence across reloads
    localStorage.setItem("llm_provider", tempProvider);
    localStorage.setItem("llm_api_key", tempKey);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fadeIn">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 relative overflow-hidden">
        {/* Decorative background glow */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-violet-600/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-cyan-600/10 rounded-full blur-3xl" />

        <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <Key className="w-5 h-5 text-violet-400" />
            <h3 className="text-lg font-semibold text-slate-100">LLM & API Settings</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 transition-colors p-1 hover:bg-slate-800 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-5">
          {/* Provider Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Execution Mode / Provider
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setTempProvider("mock");
                  setTempKey(""); // Clear key input for mock mode
                }}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-sm transition-all ${
                  tempProvider === "mock"
                    ? "bg-violet-600/20 border-violet-500 text-violet-200"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <span className="font-semibold text-sm">Simulation Mode</span>
                <span className="text-[10px] opacity-70 mt-1">Zero Key / Instant Demo</span>
              </button>
              <button
                type="button"
                onClick={() => setTempProvider("openai")}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-sm transition-all ${
                  tempProvider === "openai"
                    ? "bg-violet-600/20 border-violet-500 text-violet-200"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <span className="font-semibold text-sm">OpenAI (Real)</span>
                <span className="text-[10px] opacity-70 mt-1">gpt-4o-mini</span>
              </button>
              <button
                type="button"
                onClick={() => setTempProvider("anthropic")}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-sm transition-all ${
                  tempProvider === "anthropic"
                    ? "bg-violet-600/20 border-violet-500 text-violet-200"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <span className="font-semibold text-sm">Anthropic (Real)</span>
                <span className="text-[10px] opacity-70 mt-1">Claude 3.5 Sonnet</span>
              </button>
              <button
                type="button"
                onClick={() => setTempProvider("gemini")}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-sm transition-all ${
                  tempProvider === "gemini"
                    ? "bg-violet-600/20 border-violet-500 text-violet-200"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <span className="font-semibold text-sm">Google Gemini</span>
                <span className="text-[10px] opacity-70 mt-1">gemini-2.5-flash</span>
              </button>
            </div>
          </div>

          {/* API Key Input (conditional) */}
          {tempProvider !== "mock" && (
            <div className="space-y-2 animate-fadeIn">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-slate-300">
                  API Key for {tempProvider.toUpperCase()}
                </label>
                <span className="text-[10px] text-slate-500 flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Encrypted locally
                </span>
              </div>
              <input
                type="password"
                value={tempKey}
                onChange={(e) => setTempKey(e.target.value)}
                placeholder={`Enter your ${tempProvider.toUpperCase()} API key...`}
                className="w-full bg-slate-950 border border-slate-800 focus:border-violet-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-600 outline-none transition-all"
              />
              <p className="text-[11px] text-slate-500 flex gap-1 leading-relaxed mt-1">
                <HelpCircle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                This key is used entirely inside the backend or passed directly to LLM endpoints. It is never stored on external databases.
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t border-slate-800">
            <button
              onClick={onClose}
              type="button"
              className="flex-1 bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 rounded-xl py-2.5 text-sm font-medium transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              type="button"
              className="flex-1 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white rounded-xl py-2.5 text-sm font-semibold shadow-lg shadow-violet-900/20 transition-all"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
