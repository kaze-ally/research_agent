# main.py
from dotenv import load_dotenv
# main.py - change import line
from graph.graph import graph_cli as graph
import os

# Load .env from the script's directory (works from any working directory)
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def run_research(topic: str):
    print(f"\n[*] Starting research on: {topic}\n")
    
    initial_state = {
        "topic": topic,
        "research_notes": "",
        "fact_check_feedback": "",
        "final_report": "",
        "iteration_count": 0,
        "quality_approved": False
    }

    final_state = graph.invoke(initial_state)

    print(f"\n✅ Completed in {final_state['iteration_count']} iteration(s)\n")
    print("=" * 60)
    print(final_state["final_report"])

    # Save to file
    os.makedirs("output", exist_ok=True)
    with open("output/report.md", "w") as f:
        f.write(final_state["final_report"])
    print("\n📄 Report saved to output/report.md")

if __name__ == "__main__":
    # Human-in-the-loop workflow with LangSmith tracing
    topic = "Latest developments in AI agents 2026"
    print(f"\n[*] Starting research on: {topic}\n")
    print("[*] LangSmith Tracing: ENABLED (check your dashboard)\n")
    
    initial_state = {
        "topic": topic,
        "research_notes": "",
        "fact_check_feedback": "",
        "final_report": "",
        "iteration_count": 0,
        "quality_approved": False
    }
    
    config = {"configurable": {"thread_id": "research-1"}}

    # Run until the interrupt (before writer node)
    try:
        graph.invoke(initial_state, config=config)
    except Exception as e:
        # Expected: graph pauses with interrupt_before=["writer"]
        pass

    # Show human what the fact-checker approved
    state = graph.get_state(config)
    print("\n" + "="*60)
    print("--- RESEARCH NOTES FOR YOUR REVIEW (Fact-Checker Approved) ---")
    print("="*60)
    print(state.values["research_notes"])
    
    if state.values.get("fact_check_feedback"):
        print("\n[!] Fact-Checker Issues (if any):")
        print(state.values["fact_check_feedback"])

    input("\n[?] Press Enter to approve and generate final report...")

    # Resume from where it paused (triggers writer node)
    print("\n[*] Resuming workflow... Generating final report...\n")
    final_state = graph.invoke(None, config=config)
    
    print(f"\n✅ Completed in {final_state['iteration_count']} iteration(s)\n")
    print("="*60)
    print(final_state["final_report"])

    # Save to file
    os.makedirs("output", exist_ok=True)
    with open("output/report.md", "w") as f:
        f.write(final_state["final_report"])
    print("\n📄 Report saved to output/report.md")
    print("\n[*] View LangSmith traces: https://smith.langchain.com")