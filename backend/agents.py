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
        Orchestrates CrewAI collaboration between Researcher, Reviewer, Analyst, and Writer.
        Yields serialized JSON events streamed to the client via SSE.
        """
        yield self._format_event("status", {"agent": "Researcher", "status": "thinking", "progress": 10})
        await asyncio.sleep(1.0)

        # 1. Start CrewAI Orchestration
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "CrewAI Startup",
            "message": f"Initializing CrewAI with 4 Agents (Researcher, Reviewer, Analyst, Writer) in sequential pipeline. Tone: '{self.tone}'."
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

            # 2. Define the CrewAI Agents
            researcher_agent = Agent(
                role="Senior Real Estate Trend Analyst",
                goal=f"Perform exhaustive research on local and global real estate developments matching: '{self.query}'",
                backstory="You are a data-driven property trend investigator. You scour transaction lists, regional filings, average yields, and demographic shifting indexes to extract high-fidelity market reports.",
                llm=llm_instance,
                verbose=True,
                allow_delegation=False
            )

            reviewer_agent = Agent(
                role="Real Estate Audit & Compliance Officer",
                goal="Critique property research reports for inflation adjustments, asset segregation, and legal disclosures.",
                backstory="You are a meticulous auditor. You cross-examine transaction statistics, ensure CAGR calculations note inflation, and append necessary regulatory advice disclosures.",
                llm=llm_instance,
                verbose=True,
                allow_delegation=False
            )

            analyst_agent = Agent(
                role="Consumer Psychology & Property Strategist",
                goal="Deconstruct refined property reports into high-converting consumer hooks, core angles, and structural storyboards.",
                backstory="You are a master of social media psychology. You convert cold housing metrics into compelling, scroll-stopping narratives.",
                llm=llm_instance,
                verbose=True,
                allow_delegation=False
            )

            writer_agent = Agent(
                role="Creative Property Copywriter & Midjourney Visualizer",
                goal=f"Translate content strategies into polished, high-converting Instagram post copy utilizing tone: '{self.tone}' and descriptive Midjourney prompt templates.",
                backstory="You are a world-class real estate copywriter. You specialize in viral bullet formatting, persuasive Calls to Action, relevant hashtags, and cinematic AI-art instructions.",
                llm=llm_instance,
                verbose=True,
                allow_delegation=False
            )

            # 3. Define the CrewAI Sequential Tasks
            yield self._format_event("status", {"agent": "Researcher", "status": "running_task", "progress": 20})
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

            # To capture intermediate outputs cleanly in an async stream, we run them in sequence
            # using CrewAI's step execution or run tasks sequentially. Let's trigger them.
            loop = asyncio.get_event_loop()

            # Step A: Run Research
            crew_research = Crew(agents=[researcher_agent], tasks=[task_research], verbose=True)
            research_output = await loop.run_in_executor(None, crew_research.kickoff)
            research_text = str(research_output)

            yield self._format_event("log", {
                "agent": "Researcher",
                "action": "Research Completed",
                "message": "CrewAI Researcher completed initial market research report."
            })
            yield self._format_event("result", {"stage": "research", "data": research_text})

            # Step B: Run Review
            yield self._format_event("status", {"agent": "Reviewer", "status": "thinking", "progress": 40})
            yield self._format_event("log", {
                "agent": "Reviewer",
                "action": "Compliance Task",
                "message": "CrewAI Reviewer starting audit of the Researcher's report..."
            })
            await asyncio.sleep(1.0)

            task_review = Task(
                description=f"Critique and refine this research document. Verify that rental yields distinguish landed vs condos, adjust CAGR values for net-inflation, list specific source credentials, and append a general financial disclaimer.\n\nResearch to Audit:\n{research_text}",
                expected_output="An audited real estate intelligence report with revisions, inflation factors, and proper disclaimers.",
                agent=reviewer_agent
            )

            crew_review = Crew(agents=[reviewer_agent], tasks=[task_review], verbose=True)
            review_output = await loop.run_in_executor(None, crew_review.kickoff)
            review_text = str(review_output)

            yield self._format_event("log", {
                "agent": "Reviewer",
                "action": "Audit Completed",
                "message": f"Review complete. Feedback: '{review_text[:100]}...'"
            })
            yield self._format_event("result", {"stage": "review", "data": review_text})

            # Step C: Run Analyst
            yield self._format_event("status", {"agent": "Analyst", "status": "thinking", "progress": 60})
            yield self._format_event("log", {
                "agent": "Analyst",
                "action": "Strategy Task",
                "message": "CrewAI Analyst is mapping user personas, visual carousels, and emotional hooks..."
            })
            await asyncio.sleep(1.0)

            task_analysis = Task(
                description=f"Construct a compelling Instagram Strategy. Detail the Target Audience, the core social angle, and psychology hooks. Then outline a 5-slide Carousel storyboard layout based on this audited research:\n\n{review_text}",
                expected_output="A comprehensive 5-slide carousel storyboard, core angles, and psychology hooks outline.",
                agent=analyst_agent
            )

            crew_analysis = Crew(agents=[analyst_agent], tasks=[task_analysis], verbose=True)
            analysis_output = await loop.run_in_executor(None, crew_analysis.kickoff)
            analysis_text = str(analysis_output)

            yield self._format_event("log", {
                "agent": "Analyst",
                "action": "Strategy Finalized",
                "message": "CrewAI Analyst formulated target persona, slide headlines, and scroll-stoppers."
            })
            yield self._format_event("result", {"stage": "analysis", "data": analysis_text})

            # Step D: Run Writer
            yield self._format_event("status", {"agent": "Writer", "status": "thinking", "progress": 80})
            yield self._format_event("log", {
                "agent": "Writer",
                "action": "Copywriting Task",
                "message": f"CrewAI Writer is drafting high-converting social caption using tone: '{self.tone}'..."
            })
            await asyncio.sleep(1.0)

            task_writing = Task(
                description=f"Draft the finalized Instagram copy. Use an attention-grabbing pattern-interrupt hook, structured body spacing with emojis, a strong CTA, a bundle of 15+ real estate hashtags, and a detailed DALL-E/Midjourney cinematic photo prompt representing the cover slide. Based on this strategy:\n\n{analysis_text}",
                expected_output=f"A viral Instagram post caption with bullet spacing, hashtags, and a Midjourney prompt.",
                agent=writer_agent
            )

            crew_writer = Crew(agents=[writer_agent], tasks=[task_writing], verbose=True)
            writer_output = await loop.run_in_executor(None, crew_writer.kickoff)
            writer_text = str(writer_output)

            yield self._format_event("log", {
                "agent": "Writer",
                "action": "Writing Completed",
                "message": "CrewAI Writer successfully completed Instagram caption and Midjourney storyboard prompt!"
            })
            yield self._format_event("result", {"stage": "writer", "data": writer_text})

            # Finalize CrewAI Sequential Execution
            yield self._format_event("status", {"agent": "Done", "status": "idle", "progress": 100})
            yield self._format_event("done", {"message": "CrewAI agents successfully orchestrated. Job Complete!"})

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

        research_body = f"""### MARKET INTELLIGENCE REPORT: Property Estate Trends for '{self.query}'

1. **Current Transaction Climate**:
   - Volume and buyer appetite have shifted towards {location_adj}.
   - Premium central district property prices have stabilized, but rental demand remains exceptionally strong, yielding a tight but stable market index.
   - A significant percentage of active buyers are focusing on "{prop_type}" to optimize entry cost and yield profiles.

2. **Yields & Returns in {location}**:
   - Average rental yield in metropolitan suburban hubs/specialized sectors ({prop_type}) is holding steady at **{yield_range}**.
   - Prime residential asset price appreciation has averaged **{cagr} CAGR** over the last 5 years (nominal).

3. **Demographics**:
   - {demographics}
   - Older demographics looking to downsize are actively seeking secure, low-maintenance boutique spaces with premium management services.

*Sources: {sources}, Global Estate Analytics 2026, National Housing Registry.*"""

        yield self._format_event("result", {"stage": "research", "data": research_body})

        # 2. Simulated Reviewer logs
        yield self._format_event("status", {"agent": "Reviewer", "status": "thinking", "progress": 35})
        yield self._format_event("log", {
            "agent": "Reviewer",
            "action": "Compliance Check",
            "message": f"Auditing metrics in {location}. Reviewing rental yields and CAGR for landed properties vs condos."
        })
        await asyncio.sleep(1.3)
        yield self._format_event("log", {
            "agent": "Reviewer",
            "action": "Feedback Drafted",
            "message": "Researcher must adjust CAGR calculations for inflation and add proper advisory disclosures."
        })
        await asyncio.sleep(1.3)

        critique = f"""**CRITIQUE & COMPLIANCE FEEDBACK**:
- **Source Verification**: The {yield_range} rental yields are accurate for {prop_type} in {location}, but landed single-family properties are closer to {yields_landed}. This must be specified.
- **CAGR Accuracy**: The CAGR figures of {cagr} are nominal. Please specify that this is raw appreciation and note the net-inflation rate (currently {inflation}).
- **Compliance Rule**: Real estate advisory disclosure warning must be noted. We are providing general insights, not certified financial or investment advice.
- **Tone check**: Ensure the output does not make speculative promises about guaranteed returns."""

        yield self._format_event("result", {"stage": "review", "data": critique})

        # 2.5 Simulated Revision
        yield self._format_event("status", {"agent": "Researcher", "status": "revising", "progress": 50})
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "Data Revision",
            "message": f"Adjusting figures based on Compliance review: Separating {prop_type} yields and calculating net CAGR."
        })
        await asyncio.sleep(1.3)

        revised_research = research_body + f"\n\n[REVISED WITH COMPLIANCE SUGGESTIONS]\n- Landed property rental yields in {location} clarified (approx {yields_landed}).\n- Adjusted prime appreciation ({cagr} nominal) for inflation ({inflation} net inflation index).\n- Disclaimer: General market information. Not financial advisory."
        yield self._format_event("result", {"stage": "research", "data": revised_research})

        # 3. Simulated Analyst logs
        yield self._format_event("status", {"agent": "Analyst", "status": "thinking", "progress": 65})
        yield self._format_event("log", {
            "agent": "Analyst",
            "action": "Content Framing",
            "message": f"Designing visual hooks for {location}. Decided on: '{prop_type} yields vs. Downtown luxury vanity'."
        })
        await asyncio.sleep(1.3)
        yield self._format_event("log", {
            "agent": "Analyst",
            "action": "Storyboard Ready",
            "message": f"Proposed a 5-slide carousel layout focusing on young buyer shifts in {location.split(',')[0]}."
        })
        await asyncio.sleep(1.3)

        analysis = f"""### STRATEGIC SOCIAL OUTLINE: "{self.query}"

**1. Target Audience Persona**:
- {demographics}

**2. Content Core Angle**:
- {core_message}

**3. Psychology Hooks**:
- **Pattern Interrupt**: "Stop looking at city-core vanity assets. The real smart money is looking elsewhere."
- **Authority Hook**: Backed by actual {sources.split(',')[0]} statistics and inflation-adjusted CAGR.

**4. Suggested Visual Layout**:
- **Carousel Post (5 Slides)**:
  - Slide 1: Hook Headline + High-quality image of a modern {prop_type} build in {location}.
  - Slide 2: The comparison graph (suburban/specialized yield {yield_range} vs. city-core {yields_landed}).
  - Slide 3: Demographic shift: Why buyers are choosing flexible, work-ready homes.
  - Slide 4: Real math: How inflation ({inflation}) affects your nominal {cagr} asset appreciation.
  - Slide 5: Call to Action (CTA) pointing to the link in bio."""

        yield self._format_event("result", {"stage": "analysis", "data": analysis})

        # 4. Simulated Writer logs
        yield self._format_event("status", {"agent": "Writer", "status": "thinking", "progress": 85})
        yield self._format_event("log", {
            "agent": "Writer",
            "action": "Drafting Post Copy",
            "message": f"Formulating caption using tone: '{self.tone}' and building the call-to-action."
        })
        await asyncio.sleep(1.3)
        yield self._format_event("log", {
            "agent": "Writer",
            "action": "Creating AI Art Recipe",
            "message": f"Formulating detailed Midjourney prompts with {prop_type} architectural aesthetics."
        })
        await asyncio.sleep(1.3)

        tone_prefix = "💼 **MARKET REPORT** 💼" if self.tone == "professional" else "🔥 **HOT TAKE** 🔥"
        writing = f"""{tone_prefix}
**Is city-center vanity blinding you to the real real estate cash cows in {location.split(',')[0]}?** 👇

Everyone dreams of owning the most expensive downtown penthouse. But if you’re looking at the actual MATH, specialized {prop_type} assets are quietly walking away with the prize. 🏆

Here is what the latest market intelligence shows:

📊 **The Yield Gap**: While premium city-center luxury units average a tight {yields_landed} rental yield, mature regional {prop_type} developments are holding strong between **{yield_range}**!

🌱 **The Smart Buyer Shift**: {demographics.split(' prioritizing')[0]} aren't looking for gilded elevators—they want sustainable green-materials, smart-home integration, and flexible workspace floorplans.

📈 **The Appreciation Factor**: Over the last 5 years, prime assets in this sector enjoyed a **{cagr} CAGR** (nominal). When adjusted for a {inflation} net inflation index, your real asset value is still growing exceptionally strong.

💡 **The Bottom Line**: Don’t buy for vanity; buy for utility and yield. Specialized properties are offering premium returns at a fraction of the entry cost.

What's your move? Are you staying downtown, or heading towards {prop_type}? Let us know in the comments! 💬

---

### 🏷️ HASHTAG BUNDLE (Copy & Paste):
#PropertyInvesting #{location.split(',')[0].replace(' ', '')}RealEstate #RealEstateTrends #{prop_type.replace(' & ', '').replace(' ', '')} #PassiveIncome #RentalYield #HomeBuyingGuide #SmartHomeDesign #PropertyMarket2026 #WealthBuilding #FinancialFreedom #InvestmentAdviceDisclosure #EstatePlanning

---

### 🎨 IMAGE GENERATION PROMPT:
**Prompt for Midjourney / DALL-E 3**:
*{photo_prompt_details} Shot on 35mm lens, realistic, photorealistic, cinematic lighting, 8k resolution, architectural digest style. --ar 4:5*"""

        yield self._format_event("result", {"stage": "writer", "data": writing})

        # Done
        yield self._format_event("status", {"agent": "Done", "status": "idle", "progress": 100})
        yield self._format_event("done", {"message": "All agents have completed their tasks!"})
