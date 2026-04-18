# graph/nodes.py
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from .state import ResearchState
from tools.search import search_web as search


# Defer LLM initialization until first use
_llm = None

def get_llm():
    """Lazy-load the LLM."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
    return _llm


# ── AGENT 1: Researcher ──────────────────────────────────────────
def researcher_node(state: ResearchState):
    print("\n[Agent] 🔬 RESEARCHER NODE RUNNING")
    # Convert state to dict to access fields
    if isinstance(state, dict):
        state_dict = state
    else:
        # Convert TypedDict-like object to dict by using getattr for each field
        state_dict = {
            "topic": getattr(state, "topic", ""),
            "research_notes": getattr(state, "research_notes", ""),
            "fact_check_feedback": getattr(state, "fact_check_feedback", ""),
            "final_report": getattr(state, "final_report", ""),
            "iteration_count": getattr(state, "iteration_count", 0),
            "quality_approved": getattr(state, "quality_approved", False),
        }
    
    feedback = state_dict.get("fact_check_feedback", "")
    
    # If looping back, include the fact-checker's feedback in the prompt
    feedback_prompt = f"\n\nPrevious attempt had issues: {feedback}\nPlease fix these specifically." if feedback else ""

    search_results = search(state_dict["topic"])

    messages = [
        SystemMessage(content="""You are a Lead Researcher. 
        Research the given topic thoroughly using the provided search results.
        Always cite your sources with URLs.
        Be factual and specific — avoid vague claims."""),
        HumanMessage(content=f"""
        Topic: {state_dict['topic']}
        Search Results: {search_results}
        {feedback_prompt}
        
        Write detailed research notes with sources.
        """)
    ]

    response = get_llm().invoke(messages)

    iteration_count = state_dict.get("iteration_count", 0)
    
    return {
        **state_dict,
        "research_notes": response.content,
        "iteration_count": iteration_count + 1
    }


# ── AGENT 2: Fact Checker ────────────────────────────────────────
def fact_checker_node(state: ResearchState):
    # Convert state to dict
    if isinstance(state, dict):
        iteration = state.get("iteration_count", 0)
    else:
        iteration = getattr(state, "iteration_count", 0)
    print(f"\n[Agent] ✅ FACT-CHECKER NODE RUNNING (Iteration {iteration})")
    if isinstance(state, dict):
        state_dict = state
    else:
        state_dict = {
            "topic": getattr(state, "topic", ""),
            "research_notes": getattr(state, "research_notes", ""),
            "fact_check_feedback": getattr(state, "fact_check_feedback", ""),
            "final_report": getattr(state, "final_report", ""),
            "iteration_count": getattr(state, "iteration_count", 0),
            "quality_approved": getattr(state, "quality_approved", False),
        }
    
    messages = [
        SystemMessage(content="""You are a strict Fact-Checker.
        Analyze research notes and check for:
        1. Unsupported claims (no source cited)
        2. Vague statements like "many experts say"
        3. Logical inconsistencies
        
        Respond in this exact format:
        APPROVED: true/false
        ISSUES: (list issues if not approved, or "None")"""),
        HumanMessage(content=f"""
        Research Notes to verify:
        {state_dict['research_notes']}
        """)
    ]

    response = get_llm().invoke(messages)
    content = response.content

    # Parse the structured response
    approved = "APPROVED: true" in content.lower()
    issues = content.split("ISSUES:")[-1].strip() if "ISSUES:" in content else ""

    return {
        **state_dict,
        "quality_approved": approved,
        "fact_check_feedback": issues
    }


# ── AGENT 3: Technical Writer ────────────────────────────────────
def writer_node(state: ResearchState):
    print("\n[Agent] ✍️ WRITER NODE RUNNING - Generating Final Report")
    # Convert state to dict
    if isinstance(state, dict):
        state_dict = state
    else:
        state_dict = {
            "topic": getattr(state, "topic", ""),
            "research_notes": getattr(state, "research_notes", ""),
            "fact_check_feedback": getattr(state, "fact_check_feedback", ""),
            "final_report": getattr(state, "final_report", ""),
            "iteration_count": getattr(state, "iteration_count", 0),
            "quality_approved": getattr(state, "quality_approved", False),
        }
    
    messages = [
        SystemMessage(content="""You are a Technical Writer.
        Transform research notes into a clean, structured report.
        Use markdown formatting with headers, bullet points, and a sources section.
        Tone: professional but readable."""),
        HumanMessage(content=f"""
        Research Notes:
        {state_dict['research_notes']}
        
        Write a complete report with:
        - Executive Summary
        - Key Findings
        - Detailed Analysis  
        - Sources
        """)
    ]

    response = get_llm().invoke(messages)

    return {
        **state_dict,
        "final_report": response.content
    }