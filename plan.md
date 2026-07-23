# Multi-Agent Property Research & Instagram Post Writer - Implementation Plan

We are building a multi-agent system where four distinct agents collaborate to research topics and write high-converting Instagram posts. The application features a React (Vite + Tailwind CSS) frontend and a FastAPI (Python) backend, communicating via Server-Sent Events (SSE) for real-time progress updates.

## 1. Multi-Agent Collaboration Workflow

```
[ User Query ] (e.g., "Top property estate trends in 2026")
      │
      ▼
┌──────────────┐      ┌──────────────┐
│  Researcher  │ ───> │   Reviewer   │ (Checks alignment/facts, requests corrections if needed)
└──────────────┘      └──────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │   Analyst    │ (Distills facts into key angles & hook strategies)
                      └──────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │    Writer    │ ───> [ Final Output: IG Post + Visual Prompt ]
                      └──────────────┘
```

Each agent has a specific persona, instructions, and outputs:
1. **Researcher**: Sweeps search sources to collect latest trends, data, and audience insights.
2. **Reviewer**: Evaluates the research. In simulation mode or real-LLM mode, it acts as a critic, identifying gaps or recommending refinement.
3. **Analyst**: Distills the research into a solid content strategy, producing a proposed topic, main message, hooks, and structure.
4. **Writer**: Crafts the actual Instagram post copy (engaging hook, structured body, strong call-to-action, 15+ highly relevant hashtags, and a detailed DALL-E/Midjourney image generation prompt).

---

## 2. Directory Structure

```
/home/coder/calvinauhc002/
├── backend/
│   ├── main.py             # FastAPI App, SSE setup, CORS
│   ├── agents.py           # Multi-agent logic, LLM system prompts, mock generator
│   └── requirements.txt    # Python dependencies (fastapi, uvicorn, pydantic, openai, google-genai, anthropic)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SettingsModal.tsx     # API Key & Mode config
│   │   │   ├── AgentLogStream.tsx   # Real-time multi-agent conversation UI
│   │   │   ├── InputPanel.tsx       # Prompt, tone, and action buttons
│   │   │   └── OutputViewports.tsx  # Tabs for Research, Analyst Structure, and Final Post
│   │   ├── App.tsx                  # Main layout and SSE connection state
│   │   ├── index.css                # Tailwind base styles
│   │   └── main.tsx                 # React entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
└── README.md               # Quickstart guide
```

---

## 3. Communication Channel: Server-Sent Events (SSE)

To provide an immersive multi-agent experience, we need a real-time log. Instead of the user waiting for a single long API call, the backend will stream events in real-time as the agents work:
- `event: researcher` -> "Researcher is searching for trending Singapore property topics..."
- `event: reviewer` -> "Reviewer is validating data accuracy..."
- `event: analyst` -> "Analyst is distilling research into 3 major angles..."
- `event: writer` -> "Writer is crafting the hook and selecting hashtags..."
- `event: status` -> Updates the currently active agent.
- `event: result` -> Pushes the intermediate or final outputs (research text, analyst structure, final post).
- `event: done` -> Finalizes the stream.

---

## 4. Dual-Mode execution: Simulation vs. Real LLM

To guarantee a seamless experience out-of-the-box, the backend will support:
- **Simulation Mode**: Uses high-quality, dynamically tailored real estate research, reviewer critiques, analysis, and writing samples based on the user's input query. This lets the user see the agent chatter and layout instantly with zero configuration or cost!
- **Real LLM Mode**: If an API key is provided (OpenAI, Anthropic, or Gemini) in the settings modal or `.env` file, the backend will use the official SDKs to instantiate real LLM agents who will perform the actual web search simulation, reviews, content structuring, and writing.

---

## 5. Development Steps

1. **Backend Initialization**: Create files and install Python packages.
2. **Core Agent Classes**: Write prompts and prompt execution logic in `backend/agents.py`.
3. **SSE Connection**: Build `/api/generate` endpoint using `EventSourceResponse` style stream in `backend/main.py`.
4. **Vite + React Setup**: Scaffold React frontend, configure Tailwind CSS.
5. **Build Dashboard UI**: Code input forms, interactive timeline (with typing indicators, avatar icons for Researcher 🔍, Reviewer 🧐, Analyst 📊, Writer ✍️), settings, and formatted outputs.
6. **Frontend Integration**: Hook up `EventSource` in React to point to FastAPI.
7. **Testing & Polishing**: Ensure smooth rendering of emojis, markdown output, copy-to-clipboard actions, and error handling.

---

## 6. Bug Fixes & Premium Enhancements Plan (Active Work)

We are addressing several issues and implementing enhancements to elevate the dashboard to production-ready status:

### Task 1: Fix the SSE Event-Stream Formatting Bug
* **The Issue**: In `backend/agents.py`, `_format_event` generates raw strings like `"event: status\ndata: ...\n\n"`. `EventSourceResponse` in `sse-starlette` expects a generator yielding dictionaries with `"event"` and `"data"` keys. When given raw strings, it wraps them entirely in a default `"message"` data event, which prevents custom frontend event listeners like `eventSource.addEventListener("status")` from ever firing.
* **The Solution**: 
  - Refactor `_format_event` in `backend/agents.py` to return dictionaries: `{"event": event_type, "data": json.dumps(data)}`.
  - Refactor `MultiAgentOrchestrator.run()` and `_run_simulated_flow()` to yield these dictionaries directly to `EventSourceResponse`.

### Task 2: Enhance Simulation Mode with Dynamic, Query-Adapted Content
* **The Issue**: Currently, Simulation Mode outputs the exact same Singapore condo statistics and yields regardless of the user's query.
* **The Solution**:
  - Implement a query analyzer in `MultiAgentOrchestrator._run_simulated_flow` that parses the topic for location keywords (e.g., London, New York, Tokyo, Sydney) and property types (e.g., commercial, residential, co-living, industrial, suburban).
  - Dynamically populate yields, transaction trends, authority sources (e.g., URA, Zillow, UK Land Registry), demographic shifts, visual descriptors, and tone-specific copy based on the parsed query.
  - This provides a zero-key, high-fidelity experience that behaves exactly like a real LLM but runs instantly and free.

### Task 3: Configure Premium UI CSS Animations for Tailwind v4
* **The Issue**: Frontend classes like `animate-fadeIn`, `animate-pulse-slow`, and `animate-bounce-slow` are referenced but not fully styled/defined in Tailwind v4 configuration.
* **The Solution**:
  - Define custom `@keyframes` and animation utility classes (`.animate-fadeIn`, `.animate-pulse-slow`, and `.animate-bounce-slow`) directly in `frontend/src/index.css` using modern, native CSS transitions.

### Task 4: End-to-End System Verification
* **The Issue**: Guarantee absolute correctness.
* **The Solution**:
  - Verify that the FastAPI backend starts, restarts, and handles SSE correctly.
  - Use `curl` to test the custom event structure.
  - Check the frontend console to ensure no errors are thrown during log streaming.
