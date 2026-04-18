# graph/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import ResearchState
from graph.nodes import researcher_node, fact_checker_node, writer_node

def should_loop_back(state: ResearchState):
    if isinstance(state, dict):
        approved = state.get("quality_approved", False)
        count = state.get("iteration_count", 0)
    else:
        approved = getattr(state, "quality_approved", False)
        count = getattr(state, "iteration_count", 0)

    if approved or count >= 3:
        return "writer"
    return "researcher"

def build_graph(human_in_loop: bool = False):
    builder = StateGraph(ResearchState)
    builder.add_node("researcher", researcher_node)
    builder.add_node("fact_checker", fact_checker_node)
    builder.add_node("writer", writer_node)
    builder.set_entry_point("researcher")
    builder.add_edge("researcher", "fact_checker")
    builder.add_conditional_edges("fact_checker", should_loop_back)
    builder.add_edge("writer", END)

    if human_in_loop:
        memory = MemorySaver()
        return builder.compile(
            checkpointer=memory,
            interrupt_before=["writer"]
        )
    else:
        return builder.compile()  # No checkpointer for API mode

# Two graph instances
graph = build_graph(human_in_loop=False)   # Used by api.py
graph_cli = build_graph(human_in_loop=True) # Used by main.py