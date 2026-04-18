# api.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uuid
# Load env from script's directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

from graph.graph import graph

app = FastAPI(
    title="Multi-Agent Researcher",
    description="Self-correcting AI research agent with reflection loop",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response Models ──────────────────────────────────────
class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    topic: str
    report: str
    iterations: int
    status: str

# ── Routes ──────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "online", "agent": "multi-agent-researcher"}

@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    try:
        import uuid
        initial_state = {
            "topic": request.topic,
            "research_notes": "",
            "fact_check_feedback": "",
            "final_report": "",
            "iteration_count": 0,
            "quality_approved": False,
        }
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        final_state = graph.invoke(initial_state, config=config)

        return ResearchResponse(
            topic=request.topic,
            report=final_state["final_report"],
            iterations=final_state["iteration_count"],
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Web UI served here — Step 3 will fill this in
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multi-Agent Researcher</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; min-height: 100vh; }
            
            .header { background: #1a1d27; border-bottom: 1px solid #2a2d3e; padding: 20px 40px; display: flex; align-items: center; gap: 12px; }
            .header h1 { font-size: 1.4rem; font-weight: 600; color: #fff; }
            .badge { background: #4f46e5; color: white; font-size: 0.7rem; padding: 3px 8px; border-radius: 20px; font-weight: 500; }
            
            .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
            
            .search-box { background: #1a1d27; border: 1px solid #2a2d3e; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
            .search-box label { font-size: 0.85rem; color: #888; margin-bottom: 8px; display: block; }
            .input-row { display: flex; gap: 12px; }
            input[type="text"] { 
                flex: 1; background: #0f1117; border: 1px solid #2a2d3e; 
                color: #e0e0e0; padding: 12px 16px; border-radius: 8px; 
                font-size: 1rem; outline: none; transition: border 0.2s;
            }
            input[type="text"]:focus { border-color: #4f46e5; }
            button { 
                background: #4f46e5; color: white; border: none; 
                padding: 12px 24px; border-radius: 8px; font-size: 1rem; 
                cursor: pointer; font-weight: 500; transition: background 0.2s; white-space: nowrap;
            }
            button:hover { background: #4338ca; }
            button:disabled { background: #2a2d3e; color: #555; cursor: not-allowed; }

            .status-bar { display: none; background: #1a1d27; border: 1px solid #2a2d3e; border-radius: 8px; padding: 16px 20px; margin-bottom: 24px; align-items: center; gap: 12px; }
            .spinner { width: 18px; height: 18px; border: 2px solid #2a2d3e; border-top-color: #4f46e5; border-radius: 50%; animation: spin 0.8s linear infinite; flex-shrink: 0; }
            @keyframes spin { to { transform: rotate(360deg); } }
            .status-text { font-size: 0.9rem; color: #888; }

            .result-box { display: none; background: #1a1d27; border: 1px solid #2a2d3e; border-radius: 12px; overflow: hidden; }
            .result-header { padding: 16px 24px; border-bottom: 1px solid #2a2d3e; display: flex; justify-content: space-between; align-items: center; }
            .result-header span { font-size: 0.85rem; color: #888; }
            .iterations-badge { background: #1e3a2f; color: #4ade80; font-size: 0.75rem; padding: 4px 10px; border-radius: 20px; }
            .result-content { padding: 28px; line-height: 1.7; }
            
            /* Markdown styling */
            .result-content h1 { font-size: 1.6rem; color: #fff; margin-bottom: 16px; }
            .result-content h2 { font-size: 1.2rem; color: #c0c0c0; margin: 24px 0 12px; border-bottom: 1px solid #2a2d3e; padding-bottom: 8px; }
            .result-content h3 { font-size: 1rem; color: #a0a0a0; margin: 16px 0 8px; }
            .result-content p { margin-bottom: 12px; color: #c0c0c0; }
            .result-content ul { padding-left: 20px; margin-bottom: 12px; }
            .result-content li { margin-bottom: 6px; color: #c0c0c0; }
            .result-content a { color: #4f46e5; text-decoration: none; }
            .result-content a:hover { text-decoration: underline; }
            .result-content strong { color: #e0e0e0; }

            .error-box { display: none; background: #2d1a1a; border: 1px solid #5c2a2a; border-radius: 8px; padding: 16px 20px; color: #f87171; font-size: 0.9rem; margin-bottom: 24px; }
        </style>
    </head>
    <body>

    <div class="header">
        <h1>🔬 Multi-Agent Researcher</h1>
        <span class="badge">LangGraph + Groq</span>
    </div>

    <div class="container">
        <div class="search-box">
            <label>Research Topic</label>
            <div class="input-row">
                <input type="text" id="topicInput" placeholder="e.g. Latest developments in AI agents 2026" />
                <button id="researchBtn" onclick="startResearch()">Research →</button>
            </div>
        </div>

        <div class="error-box" id="errorBox"></div>

        <div class="status-bar" id="statusBar">
            <div class="spinner"></div>
            <div>
                <div class="status-text" id="statusText">Initializing agents...</div>
                <div style="font-size:0.75rem; color:#555; margin-top:2px;">Researcher → Fact Checker → Writer (with reflection loop)</div>
            </div>
        </div>

        <div class="result-box" id="resultBox">
            <div class="result-header">
                <span id="topicLabel"></span>
                <span class="iterations-badge" id="iterationsLabel"></span>
            </div>
            <div class="result-content" id="reportContent"></div>
        </div>
    </div>

    <script>
        const messages = [
            "Researcher agent gathering sources...",
            "Fact-checker reviewing claims...",
            "Reflection loop running...",
            "Verifying sources...",
            "Writer generating report..."
        ];
        let msgIndex = 0, msgInterval;

        async function startResearch() {
            const topic = document.getElementById('topicInput').value.trim();
            if (!topic) return;

            // Reset UI
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('resultBox').style.display = 'none';
            document.getElementById('statusBar').style.display = 'flex';
            document.getElementById('researchBtn').disabled = true;
            document.getElementById('statusText').textContent = messages[0];

            msgIndex = 0;
            msgInterval = setInterval(() => {
                msgIndex = (msgIndex + 1) % messages.length;
                document.getElementById('statusText').textContent = messages[msgIndex];
            }, 3000);

            try {
                const response = await fetch('/research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic })
                });

                const data = await response.json();

                if (!response.ok) throw new Error(data.detail || 'Something went wrong');

                // Show result
                document.getElementById('topicLabel').textContent = data.topic;
                document.getElementById('iterationsLabel').textContent = `✓ ${data.iterations} iteration(s)`;
                document.getElementById('reportContent').innerHTML = marked.parse(data.report);
                document.getElementById('resultBox').style.display = 'block';

            } catch (err) {
                document.getElementById('errorBox').textContent = '⚠ ' + err.message;
                document.getElementById('errorBox').style.display = 'block';
            } finally {
                clearInterval(msgInterval);
                document.getElementById('statusBar').style.display = 'none';
                document.getElementById('researchBtn').disabled = false;
            }
        }

        document.getElementById('topicInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') startResearch();
        });
    </script>
    </body>
    </html>
        """