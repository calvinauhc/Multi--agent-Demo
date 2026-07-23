# 🏢 Real Estate AI Writer: Multi-Agent CrewAI System

An immersive, real-time dashboard powered by **CrewAI**, **FastAPI (Server-Sent Events)**, and **React (Vite + Tailwind CSS v4)**. 

The application orchestrates four distinct CrewAI agents (Researcher, Reviewer, Analyst, and Writer) to perform real estate market research and compose highly-engaging, viral, compliant Instagram posts from any user query.

---

## 🚀 Key Features

* **🤖 Dynamic CrewAI Team**: Role-playing agents (`Senior Real Estate Trend Analyst`, `Compliance Officer`, `Consumer Psychology Strategist`, and `Creative Copywriter`) collaborating sequentially using CrewAI's formal orchestration framework.
* **⚡ Live SSE Collaboration Feed**: Events are streamed in real time from the Python backend to the React frontend using Server-Sent Events (SSE). Watch the agents communicate, critiques revisions, and brainstorm hooks before writing.
* **🧪 Dual Execution Mode**:
  * **Simulation Mode**: Works instantly out of the box with zero API keys or costs. Generates realistic, dynamically tailored multi-agent workflows.
  * **Real LLM Mode**: Supports **OpenAI (GPT-4o-mini)**, **Anthropic (Claude 3.5 Sonnet)**, or **Google Gemini (Gemini 2.5 Flash)** simply by inputting an API key in the UI's Config panel.
* **📈 Rich Side-by-Side Dashboard**: Compare the final drafted post, content storyboard/carousel, and raw compliance-reviewed research report side-by-side.

---

## 📂 System Architecture & Layout

```
/home/coder/calvinauhc002/
├── backend/
│   ├── main.py             # FastAPI App, CORS, and Server-Sent Events Endpoint
│   ├── agents.py           # CrewAI Agents, Tasks, Crew setup & Simulated triggers
│   └── requirements.txt    # Python dependencies (fastapi, uvicorn, crewai, sse-starlette, etc.)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SettingsModal.tsx     # API Key & Mode config
│   │   │   ├── AgentLogStream.tsx   # SSE real-time timeline visualizer
│   │   │   ├── InputPanel.tsx       # Prompt, tone, and action triggers
│   │   │   └── OutputViewports.tsx  # Stage outputs (Research, Strategy, Post)
│   │   └── App.tsx                  # SSE EventSource state controller
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.ts
```

---

## 🛠️ Setup & Running Instructions

### 1. Start the FastAPI Backend
Open a terminal in the root directory and run:

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate

# Start Uvicorn Server (runs on http://localhost:8000)
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

*The backend includes a health check route at `http://localhost:8000/health` to confirm connections.*

### 2. Start the React Frontend
Open a separate terminal in the root directory and run:

```bash
# Navigate to frontend
cd frontend

# Run Vite dev server (runs on http://localhost:5173)
npm run dev
```

*Vite will compile and hot-reload components. Open the displayed URL in your browser to experience the dashboard!*

---

## 🤖 The CrewAI Agent Configuration

The backend is built around **CrewAI**'s agent role-playing structures:

1. **Researcher (Senior Real Estate Trend Analyst)**: 
   * *Goal*: Scours transaction registries, developer bulletins, and demographics trends to discover yields, price-appreciation CAGRs, and millennial commuter layouts.
2. **Reviewer (Real Estate Compliance & Audit Officer)**:
   * *Goal*: Audits research for nominal vs net inflation figures, filters speculative claims, and appends real estate legal disclaimers.
3. **Analyst (Consumer Psychology Strategist)**:
   * *Goal*: Translates metrics into scroll-stopping hooks (such as Pattern Interrupts and Authority hooks) and outlines a 5-slide Carousel layout.
4. **Writer (Creative Copywriter & Midjourney Visualizer)**:
   * *Goal*: Crafts the final post caption, formats it with bullet lists and emojis, adds a CTA, packages 15+ relevant hashtags, and drafts photorealistic AI art prompts.

---

## 🔒 Security & local Encryption
Your API keys are stored entirely inside your browser's local storage (`localStorage`) or loaded from your local `.env` file. They are never sent to external servers or stored in any databases.
