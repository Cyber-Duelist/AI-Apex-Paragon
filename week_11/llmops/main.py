from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json

# Import the existing evaluation logic
from eval_dashboard import evaluate_and_trace, GOLDEN_DATASET, eval_tracer

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

class EvalRequest(BaseModel):
    dataset: list[dict]

@app.post("/api/run_eval")
async def run_eval(req: EvalRequest):
    async def event_generator():
        # Clear previous traces
        eval_tracer.traces = []
        
        dataset = req.dataset
        total_questions = len(dataset)
        pass_count = 0
        total_score = 0
        
        for i, item in enumerate(dataset, 1):
            # Run the traced evaluation (Warning: sync call in async endpoint, acceptable for this demo)
            eval_result = evaluate_and_trace(item["question"], item["answer"], item["rubric"])
            
            score = eval_result.get("score", 1)
            total_score += score
            verdict = "PASS" if score >= 4 else "FAIL"
            if verdict == "PASS":
                pass_count += 1
                
            latest_trace = eval_tracer.traces[-1]
            
            payload = {
                "type": "eval_result",
                "question": item["question"],
                "score": score,
                "reasoning": eval_result.get("reasoning", "No reasoning provided"),
                "verdict": verdict,
                "latency": latest_trace["duration_ms"],
                "cost": latest_trace["estimated_cost_usd"],
                "tokens": latest_trace["total_tokens"],
                "index": i,
                "total": total_questions
            }
            yield f"data: {json.dumps(payload)}\n\n"
            
            # Let the UI breathe and show sequential progression
            await asyncio.sleep(0.1)
            
        # Compile and stream final summary metrics
        pass_rate = (pass_count / total_questions) * 100
        avg_score = total_score / total_questions
        summary = eval_tracer.get_summary()
        
        final_payload = {
            "type": "summary",
            "pass_rate": pass_rate,
            "avg_score": avg_score,
            "total_cost": float(summary["Total cost"].replace('$', '')),
            "avg_latency": summary["Avg latency"]
        }
        yield f"data: {json.dumps(final_payload)}\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")
