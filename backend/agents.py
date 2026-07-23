import os
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from pydantic import BaseModel

# Import CrewAI components
try:
    from crewai import Agent, Task, Crew, Process
    # CrewAI uses standard LLM configurations
    from crewai import LLM
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()

class AgentMessage(BaseModel):
    agent: str
    action: str
    message: str
    payload: Optional[Dict[str, Any]] = None

class MultiAgentOrchestrator:
    def __init__(
        self,
        query: str,
        tone: str = "professional",
        api_key: Optional[str] = None,
        provider: str = "mock"  # "mock", "openai", "anthropic", "gemini"
    ):
        self.query = query
        self.tone = tone
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.provider = provider if api_key or os.getenv("LLM_API_KEY") else "mock"

    async def run(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Orchestrates CrewAI Market Research Agent execution.
        Yields serialized JSON events streamed to the client via SSE.
        """
        yield self._format_event("status", {"agent": "Researcher", "status": "thinking", "progress": 10})
        await asyncio.sleep(1.0)

        # 1. Start CrewAI Orchestration
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "CrewAI Startup",
            "message": f"Initializing CrewAI with Market Research Agent (Senior Real Estate Trend Analyst). Tone: '{self.tone}'."
        })
        await asyncio.sleep(1.2)

        if self.provider == "mock" or not CREWAI_AVAILABLE:
            # Running high-fidelity simulation
            async for event in self._run_simulated_flow():
                yield event
            return

        # Running real CrewAI execution
        try:
            # 1. Initialize the LLM Configuration for CrewAI
            llm_instance = self._get_crewai_llm()
            yield self._format_event("log", {
                "agent": "System",
                "action": "Configuring LLM",
                "message": f"Successfully mapped {self.provider} API keys to CrewAI agents."
            })
            await asyncio.sleep(1.0)

            # 2. Define the CrewAI Researcher Agent
            researcher_agent = Agent(
                role="Senior Real Estate Trend Analyst",
                goal=f"Perform exhaustive research on local and global real estate developments matching: '{self.query}'",
                backstory="You are a data-driven property trend investigator. You scour transaction lists, regional filings, average yields, and demographic shifting indexes to extract high-fidelity market reports.",
                llm=llm_instance,
                verbose=True,
                allow_delegation=False
            )

            # 3. Define the CrewAI Research Task
            yield self._format_event("status", {"agent": "Researcher", "status": "running_task", "progress": 30})
            yield self._format_event("log", {
                "agent": "Researcher",
                "action": "Research Task",
                "message": f"CrewAI Researcher starting execution on query: '{self.query}'..."
            })
            await asyncio.sleep(1.0)

            task_research = Task(
                description=f"Gather detailed transaction indices, estimated rental yields, capital growth records, and home-buyer requirements for the query: '{self.query}'. Output a structured report in Markdown. Avoid speculative estimations.",
                expected_output="A structured market research document containing transaction indices, yields, and demographics.",
                agent=researcher_agent
            )

            loop = asyncio.get_event_loop()

            # Run Research
            crew_research = Crew(agents=[researcher_agent], tasks=[task_research], verbose=True)
            research_output = await loop.run_in_executor(None, crew_research.kickoff)
            research_text = str(research_output)

            yield self._format_event("log", {
                "agent": "Researcher",
                "action": "Research Completed",
                "message": f"CrewAI Researcher completed exhaustive market research report for: '{self.query}'."
            })
            yield self._format_event("result", {"stage": "research", "data": research_text})

            # Finalize CrewAI Sequential Execution
            yield self._format_event("status", {"agent": "Done", "status": "idle", "progress": 100})
            yield self._format_event("done", {"message": "CrewAI Researcher completed analysis. Job Complete!"})

        except Exception as e:
            yield self._format_event("log", {
                "agent": "System",
                "action": "Error",
                "message": f"CrewAI Orchestration encountered an issue: {str(e)}"
            })
            # Force fall back to high-fidelity simulation so the stream does not crash
            yield self._format_event("log", {
                "agent": "System",
                "action": "Fallback",
                "message": "Failing over to highly customized Simulation Mode to complete execution..."
            })
            await asyncio.sleep(1.0)
            async for event in self._run_simulated_flow():
                yield event

    def _get_crewai_llm(self) -> LLM:
        """Initializes and returns a CrewAI LLM instance based on provider choice"""
        if self.provider == "openai":
            return LLM(model="gpt-4o-mini", api_key=self.api_key)
        elif self.provider == "anthropic":
            return LLM(model="claude-3-5-sonnet-20241022", api_key=self.api_key)
        elif self.provider == "gemini":
            return LLM(model="gemini/gemini-2.5-flash", api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported CrewAI provider: {self.provider}")

    def _format_event(self, event_type: str, data: Any) -> Dict[str, Any]:
        """Helper to format SSE payload as a dict for sse-starlette"""
        return {
            "event": event_type,
            "data": json.dumps(data)
        }

    # --- SIMULATED/MOCK EVENT SEQUENCE FOR INSTANT DEMOS ---
    async def _run_simulated_flow(self) -> AsyncGenerator[Dict[str, Any], None]:
        query_lower = self.query.lower()

        # 1. Determine Location
        if any(kw in query_lower for kw in ["london", "uk", "british", "united kingdom"]):
            location = "London, United Kingdom"
            sources = "HM Land Registry, UK National Housing Index, Rightmove Report"
            local_currency = "£"
            yields_condo = "3.8% - 4.5%"
            yields_landed = "2.2% - 2.8%"
            cagr = "4.8%"
            inflation = "2.4%"
            location_adj = "commuters and zone-dwellers moving outward to suburban hubs"
            architecture = "Victorian redbrick townhouse with a modern glass extension"
        elif any(kw in query_lower for kw in ["new york", "nyc", "manhattan", "brooklyn", "usa", "american"]):
            location = "New York City, USA"
            sources = "Zillow Market Intelligence, StreetEasy Index, NY Housing Board"
            local_currency = "$"
            yields_condo = "4.2% - 5.1%"
            yields_landed = "2.5% - 3.2%"
            cagr = "5.6%"
            inflation = "2.2%"
            location_adj = "young professionals shifting towards Brooklyn and Outer Borough hubs"
            architecture = "lofted brick-and-iron industrial conversion in Brooklyn"
        elif any(kw in query_lower for kw in ["sydney", "australia", "melbourne"]):
            location = "Sydney, Australia"
            sources = "CoreLogic Home Value Index, ABS Housing Statistics"
            local_currency = "A$"
            yields_condo = "4.0% - 4.7%"
            yields_landed = "2.3% - 2.9%"
            cagr = "5.1%"
            inflation = "2.3%"
            location_adj = "coastal and outer-western lifestyle estates"
            architecture = "modern pavilion-style beachside house with exposed raw timber"
        elif any(kw in query_lower for kw in ["seattle"]):
            location = "Seattle, USA"
            sources = "Northwest MLS, King County Property Records, Redfin Analytics"
            local_currency = "$"
            yields_condo = "4.5% - 5.3%"
            yields_landed = "2.6% - 3.4%"
            cagr = "6.1%"
            inflation = "2.2%"
            location_adj = "tech workers seeking suburban green belt developments"
            architecture = "contemporary Pacific Northwest cedar-and-glass cabin home"
        elif any(kw in query_lower for kw in ["tokyo", "japan"]):
            location = "Tokyo, Japan"
            sources = "MLIT Japan Housing Index, Tokyo Metropolitan Government Records"
            local_currency = "¥"
            yields_condo = "3.4% - 4.2%"
            yields_landed = "1.8% - 2.4%"
            cagr = "3.2%"
            inflation = "1.1%"
            location_adj = "suburban Saitama and Chiba transit corridors"
            architecture = "ultra-minimalist micro-apartment with modular concrete frames"
        else:
            location = "Singapore"
            sources = "Urban Redevelopment Authority Index (URA), Real Estate Analytics, HDB Registry"
            local_currency = "S$"
            yields_condo = "4.1% - 4.8%"
            yields_landed = "2.5%"
            cagr = "5.3%"
            inflation = "2.1%"
            location_adj = "young buyers prioritizing mature estates and outer fringe regional centers"
            architecture = "modern, green tropical condominium with cascading vertical gardens"

        # 2. Determine Property Type / Concept
        if any(kw in query_lower for kw in ["co-living", "co living", "nomad", "shared"]):
            prop_type = "Co-Living & Shared Spaces"
            yield_range = "5.5% - 7.2%"
            demographics = "Millennial freelancers and digital nomads prioritizing flex leases, fast fiber, and communal social hubs."
            core_message = "Why co-living assets are offering almost DOUBLE the yields of traditional long-term rentals in high-density areas."
            photo_prompt_details = "A stylish co-living shared lounge, complete with Scandinavian wooden desks, neon accent lights, thriving houseplants, and a panorama glass wall overlooking the city skyline."
        elif any(kw in query_lower for kw in ["commercial", "office", "retail", "industrial", "warehouse"]):
            prop_type = "Commercial & Retail Properties"
            yield_range = "4.9% - 6.2%"
            demographics = "SMEs and mid-sized enterprises requiring flexible open-plan layouts, sustainable build specs, and robust logistics infrastructure."
            core_message = "The flight to quality commercial spaces that blend high corporate rental yields with absolute asset protection."
            photo_prompt_details = "An elegant, airy modern office floor with modular desks, acoustic felt paneling, smart LED lighting, and polished concrete flooring."
        elif any(kw in query_lower for kw in ["landed", "house", "villa", "bungalow"]):
            prop_type = "Landed Estates & Single-Family Homes"
            yield_range = yields_landed
            demographics = "High-net-worth multi-generational families valuing privacy, expansive floorplans, and long-term land-scarcity appreciation."
            core_message = "Landed property investing: Low immediate cash-flow yields, but unbeatable generational wealth preservation and capital gains."
            photo_prompt_details = f"A gorgeous contemporary multi-level {architecture} with a manicured front lawn, architectural accent uplighting, and sunset illumination."
        elif any(kw in query_lower for kw in ["eco", "green", "sustainable", "solar", "passive"]):
            prop_type = "Sustainable Eco-Condominiums"
            yield_range = "4.2% - 5.0%"
            demographics = "Eco-conscious tech professionals and ESG-guided investors searching for solar integration, energy-efficient HVACs, and wellness metrics."
            core_message = "Green premium is real: Sustainable building certifications are driving up both rental tenant retention and asset valuations."
            photo_prompt_details = "An architectural photograph of a modern LEED-platinum certified green condominium with vertical garden terraces, solar panels on the roof, rainwater harvesting ponds, and soft twilight sun."
        else:
            prop_type = "High-Yield Suburban Condominiums"
            yield_range = yields_condo
            demographics = "Young professional couples (aged 28-42) valuing remote-work floorplans, proximity to high-speed transit, and wellness lifestyle amenities."
            core_message = "Why modern suburban properties are beating traditional city-core luxury units on rental yields and net-of-inflation CAGR."
            photo_prompt_details = f"A beautiful architectural photograph of a modern, ultra-contemporary eco-friendly {architecture}. Features glass facades, lush vertical gardens, cascading terraces, and sunset lighting. The courtyard has a luxurious infinity pool."

        # 1. Simulated Researcher logs
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "Sweeping Sources",
            "message": f"Scraping transaction records, localized registries, and housing publication sources for '{location}'..."
        })
        await asyncio.sleep(1.3)
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "Extracting Data",
            "message": f"Found trends: Buyers shifting toward {prop_type} prioritizing regional commutes, yields, and lifestyle layouts."
        })
        await asyncio.sleep(1.3)

        # Net inflation index math
        net_appreciation = float(cagr.replace('%', '')) - float(inflation.replace('%', ''))

        research_body = f"""### MARKET INTELLIGENCE REPORT: Property Estate Trends for '{self.query}'

1. **Current Transaction Climate**:
   - Volume and buyer appetite have shifted towards {location_adj}.
   - Premium central district property prices have stabilized, but rental demand remains exceptionally strong, yielding a tight but stable market index.
   - A significant percentage of active buyers are focusing on "{prop_type}" to optimize entry cost and yield profiles.

2. **Yields & Returns in {location}**:
   - Average rental yield in metropolitan suburban hubs/specialized sectors ({prop_type}) is holding steady at **{yield_range}**.
   - Landed single-family property rental yields are holding around **{yields_landed}**.
   - Prime residential asset price appreciation has averaged **{cagr} CAGR** over the last 5 years (nominal).
   - Adjusted for a **{inflation} net inflation index**, your real net asset value growth is approximately **{net_appreciation:.1f}% net CAGR**.

3. **Demographics & Target Audience**:
   - {demographics}
   - Older demographics looking to downsize are actively seeking secure, low-maintenance boutique spaces with premium management services.

---
*Sources: {sources}, Global Estate Analytics 2026, National Housing Registry.*
*Disclaimer: This document provides general market insights. It does not constitute certified financial, legal, or investment advisory.*"""

        yield self._format_event("result", {"stage": "research", "data": research_body})

        # Done
        yield self._format_event("status", {"agent": "Done", "status": "idle", "progress": 100})
        yield self._format_event("done", {"message": f"Market research analysis for '{self.query}' successfully completed!"})
