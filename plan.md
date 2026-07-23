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
