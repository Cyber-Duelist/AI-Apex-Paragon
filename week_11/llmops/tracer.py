import os
import time
import json
import datetime
import functools
from dotenv import load_dotenv
from groq import Groq

# Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Tracer:
    """A minimal observability class to track LLM latency, tokens, and cost."""
    
    def __init__(self):
        self.traces = []
        
        # Approximate pricing per 1M tokens for LLaMA-3.3-70b on Groq
        self.PRICE_PER_MILLION_INPUT = 0.59
        self.PRICE_PER_MILLION_OUTPUT = 0.79

    def trace(self):
        """A decorator to wrap LLM calls and record their telemetry data."""
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                
                try:
                    # 1. Execute the raw Groq call
                    response = fn(*args, **kwargs)
                    success = True
                    
                    # 2. Calculate Telemetry
                    duration_ms = int((time.time() - start_time) * 1000)
                    model = response.model
                    in_tokens = response.usage.prompt_tokens
                    out_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens
                    
                    # 3. Calculate Cost
                    cost = (in_tokens / 1_000_000 * self.PRICE_PER_MILLION_INPUT) + \
                           (out_tokens / 1_000_000 * self.PRICE_PER_MILLION_OUTPUT)
                           
                    # 4. Save to trace memory
                    trace_data = {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "duration_ms": duration_ms,
                        "input_tokens": in_tokens,
                        "output_tokens": out_tokens,
                        "total_tokens": total_tokens,
                        "estimated_cost_usd": cost,
                        "model": model,
                        "success": success
                    }
                    self.traces.append(trace_data)
                    
                    # 5. Print the live trace
                    print(f"=== TRACE {len(self.traces)} ===")
                    print(f"Model    : {model}")
                    print(f"Duration : {duration_ms}ms")
                    print(f"Tokens   : {total_tokens} (in: {in_tokens}, out: {out_tokens})")
                    print(f"Cost     : ${cost:.6f}")
                    print(f"Success  : {success}\n")
                    
                    # Return just the text content so the rest of our app doesn't break
                    return response.choices[0].message.content
                    
                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.traces.append({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "duration_ms": duration_ms,
                        "success": False,
                        "error": str(e)
                    })
                    raise e
                    
            return wrapper
        return decorator

    def get_summary(self) -> dict:
        """Aggregates all trace data into a single summary."""
        total_calls = len(self.traces)
        if total_calls == 0:
            return {}
            
        avg_latency = sum(t.get('duration_ms', 0) for t in self.traces) / total_calls
        total_tokens = sum(t.get('total_tokens', 0) for t in self.traces)
        total_cost = sum(t.get('estimated_cost_usd', 0) for t in self.traces)
        
        return {
            "Total calls": total_calls,
            "Avg latency": f"{int(avg_latency)}ms",
            "Total tokens": total_tokens,
            "Total cost": f"${total_cost:.6f}"
        }

    def save_traces(self, filepath: str):
        """Saves the telemetry log to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.traces, f, indent=2)


# ==========================================
# Implementation Example
# ==========================================

# 1. Initialize the global tracer
system_tracer = Tracer()

# 2. Wrap our function with the @trace decorator
@system_tracer.trace()
def analyze_document(title: str, department: str):
    """
    Makes the raw Groq call and returns the object. 
    The decorator intercepts it, measures it, and returns the text.
    """
    prompt = f"Analyze the compliance risk of the '{title}' document for the {department} department. Be brief."
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

if __name__ == "__main__":
    print("Executing traced AI calls...\n")
    
    # 3. Call the function 3 times
    doc_1 = analyze_document("Q3 Financial Report", "Finance")
    doc_2 = analyze_document("Employee Handbook", "HR")
    doc_3 = analyze_document("Cloud Architecture Blueprint", "Engineering")
    
    # 4. Print Summary
    print("=== TRACER SUMMARY ===")
    summary = system_tracer.get_summary()
    for key, val in summary.items():
        print(f"{key:<12} : {val}")
        
    # 5. Save traces to disk
    trace_file = os.path.join(os.path.dirname(__file__), "traces.json")
    system_tracer.save_traces(trace_file)
    print(f"\n[💾 Traces saved to {trace_file}]")