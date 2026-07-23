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

    async def run(self) -> AsyncGenerator[str, None]:
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

    def _format_event(self, event_type: str, data: Any) -> str:
        """Helper to format SSE payload"""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    # --- SIMULATED/MOCK EVENT SEQUENCE FOR INSTANT DEMOS ---
    async def _run_simulated_flow(self) -> AsyncGenerator[str, None]:
        # 1. Simulated Researcher logs
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "Sweeping Sources",
            "message": "Scraping transaction records, Urban Redevelopment indices, and property publications..."
        })
        await asyncio.sleep(1.3)
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "Extracting Data",
            "message": "Found trends: buyers prioritizing green materials, suburban growth vectors, and smart spaces."
        })
        await asyncio.sleep(1.3)

        research_body = f"""### MARKET INTELLIGENCE REPORT: Property Estate Trends for '{self.query}'

1. **Current Transaction Climate**:
   - Volume has shifted towards suburban properties and mature regional centers (up 14.2% YoY).
   - Core Central District premium property prices have stabilized, but rental demand remains exceptionally strong due to a 92% occupancy index.
   - Buyers are increasingly prioritizing sustainability certifications (green building materials) and wellness amenities.

2. **Yields & Returns**:
   - Average rental yield in metropolitan suburban hubs is holding steady at 4.1% - 4.8%.
   - Prime estate price appreciation has averaged 5.3% CAGR over the last 5 years.

3. **Demographics**:
   - Millennials and Gen-Z buyers represent 38% of home purchases, focusing on "smart-home integration", "commute proximity", and flexible work-from-home layouts.
   - Downsizing older demographics are looking for highly secure, low-maintenance boutique condominiums.

*Sources: Urban Redevelopment Authority Index (URA), Global Estate Analytics 2026, National Housing Registry.*"""

        yield self._format_event("result", {"stage": "research", "data": research_body})

        # 2. Simulated Reviewer logs
        yield self._format_event("status", {"agent": "Reviewer", "status": "thinking", "progress": 35})
        yield self._format_event("log", {
            "agent": "Reviewer",
            "action": "Compliance Check",
            "message": "Auditing metrics. Reviewing rental yields and CAGR for landed properties vs condos."
        })
        await asyncio.sleep(1.3)
        yield self._format_event("log", {
            "agent": "Reviewer",
            "action": "Feedback Drafted",
            "message": "Researcher must adjust CAGR calculations for inflation and add proper advisory disclosures."
        })
        await asyncio.sleep(1.3)

        critique = """**CRITIQUE & COMPLIANCE FEEDBACK**:
- **Source Verification**: The 4.1%-4.8% rental yields are accurate for condominiums but landed properties are closer to 2.5%. This must be specified.
- **CAGR Accuracy**: The CAGR figures of 5.3% are raw. Please specify if this is nominal and note the net-inflation rate (currently 2.1%).
- **Compliance Rule**: Real estate advisory disclosure warning must be noted. We are providing general insights, not certified financial or investment advice.
- **Tone check**: Ensure the output does not make speculative promises about guaranteed returns."""

        yield self._format_event("result", {"stage": "review", "data": critique})

        # 2.5 Simulated Revision
        yield self._format_event("status", {"agent": "Researcher", "status": "revising", "progress": 50})
        yield self._format_event("log", {
            "agent": "Researcher",
            "action": "Data Revision",
            "message": "Adjusting figures based on Compliance review: Separating condo yields, calculating net CAGR."
        })
        await asyncio.sleep(1.3)

        revised_research = research_body + "\n\n[REVISED WITH COMPLIANCE SUGGESTIONS]\n- Landed property rental yields clarified (approx 2.5%).\n- Adjusted prime appreciation (5.3% nominal) for inflation (2.1% net inflation index).\n- Disclaimer: General market information. Not financial advisory."
        yield self._format_event("result", {"stage": "research", "data": revised_research})

        # 3. Simulated Analyst logs
        yield self._format_event("status", {"agent": "Analyst", "status": "thinking", "progress": 65})
        yield self._format_event("log", {
            "agent": "Analyst",
            "action": "Content Framing",
            "message": "Designing visual hooks. Decided on: 'Suburban yields vs. Downtown vanity'."
        })
        await asyncio.sleep(1.3)
        yield self._format_event("log", {
            "agent": "Analyst",
            "action": "Storyboard Ready",
            "message": "Proposed a 5-slide carousel layout focusing on young buyer shifts."
        })
        await asyncio.sleep(1.3)

        analysis = f"""### STRATEGIC SOCIAL OUTLINE: "{self.query}"

**1. Target Audience Persona**:
- High-earning young professionals (aged 28-42) looking to buy their first or second property.

**2. Content Core Angle**:
- "Suburban gems vs. Central premium": Highlighting the higher rental yield (4.1%-4.8%) of modern suburban condos compared to lower-yield city center luxury units, adjusted for inflation.

**3. Psychology Hooks**:
- **Pattern Interrupt**: "Stop looking at city penthouses. The real money is 30 minutes away."
- **Authority Hook**: Backed by actual Urban Redevelopment Authority indices and inflation-adjusted CAGR.

**4. Suggested Visual Layout**:
- **Carousel Post (5 Slides)**:
  - Slide 1: Hook Headline + High-quality image of a modern, green suburban condominium.
  - Slide 2: The comparison graph (suburban yield 4.5% vs. city center 2.8%).
  - Slide 3: Demographic shift: Why young buyers are choosing remote-work ready homes.
  - Slide 4: Real math: How inflation (2.1%) affects your nominal 5.3% asset appreciation.
  - Slide 5: Call to Action (CTA) pointing to the bio."""

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
            "message": "Formulating detailed Midjourney prompts with architectural aesthetics and cinematic sunset lighting."
        })
        await asyncio.sleep(1.3)

        tone_prefix = "💼 **MARKET REPORT** 💼" if self.tone == "professional" else "🔥 **HOT TAKE** 🔥"
        writing = f"""{tone_prefix}
**Is city-center luxury blinding you to the real real estate cash cows?** 👇

Everyone dreams of owning a penthouse in the middle of the city. But if you’re looking at the actual MATH, suburban properties are quietly walking away with the prize. 🏆

Here is what the latest market intelligence shows:

📊 **The Yield Gap**: While premium downtown condos average a tight 2.5% - 2.9% rental yield, mature suburban lifestyle hubs are holding strong between **4.1% and 4.8%**!

🌱 **The Smart-Home Shift**: 38% of active buyers are Gen-Z/Millennials. They aren't looking for gilded elevators—they want sustainable green-materials, smart-home integration, and flexible workspace floorplans.

📈 **The Appreciation Factor**: Over the last 5 years, prime suburban estates enjoyed a **5.3% CAGR** (nominal). When adjusted for a 2.1% net inflation index, your real asset value is still growing exceptionally strong.

💡 **The Bottom Line**: Don’t buy for vanity; buy for utility and yield. Suburban lifestyle properties are offering premium returns at a fraction of the entry cost.

What's your move? Are you staying in the city, or heading suburban? Let us know in the comments! 💬

---

### 🏷️ HASHTAG BUNDLE (Copy & Paste):
#PropertyInvesting #RealEstateTrends #SuburbanProperty #PassiveIncome #RentalYield #HomeBuyingGuide #SmartHomeDesign #MillennialInvestors #PropertyMarket2026 #WealthBuilding #FinancialFreedom #InvestmentAdviceDisclosure #EstatePlanning

---

### 🎨 IMAGE GENERATION PROMPT:
**Prompt for Midjourney / DALL-E 3**:
*An architectural photograph of a modern, ultra-contemporary eco-friendly suburban condominium. Features glass facades, lush vertical gardens, cascading terraces, and sunset lighting. The courtyard has a luxurious infinity pool. Shot on 35mm lens, realistic, photorealistic, cinematic lighting, 8k resolution, architectural digest style. --ar 4:5*"""

        yield self._format_event("result", {"stage": "writer", "data": writing})

        # Done
        yield self._format_event("status", {"agent": "Done", "status": "idle", "progress": 100})
        yield self._format_event("done", {"message": "All agents have completed their tasks!"})
