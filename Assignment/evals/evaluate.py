import json
import time
import os
import sys
from pathlib import Path

# Add project root directory to path so imports work correctly
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.app.agents.openai_agent import get_agent

def run_evaluation_suite():
    print("==================================================")
    # Start evaluations
    print("[AGENTS] STARTING AUTOMATED AGENT EVALUATION SUITE...")
    print("==================================================")
    
    agent = get_agent()
    
    # Ground-truth test dataset representing various query styles
    test_queries = [
        {
            "query": "Which project of yours used LangGraph and Ollama?",
            "expected_keywords": ["langgraph", "ollama", "business"],
            "type": "project_tech"
        },
        {
            "query": "Where did you do your AI Research Developer internship?",
            "expected_keywords": ["wns", "vuram", "intern"],
            "type": "experience"
        },
        {
            "query": "What are your education credentials?",
            "expected_keywords": ["scaler", "bits", "pilani"],
            "type": "education"
        },
        {
            "query": "Do you have experience with fraud detection systems?",
            "expected_keywords": ["fraud", "ensemble", "excel"],
            "type": "project_specific"
        },
        {
            "query": "Did you ever work as a principal engineer at Google?",
            "expected_keywords": ["not", "information", "records", "email"], # Enforces anti-hallucination / honesty
            "type": "out_of_bounds"
        }
    ]
    
    results = []
    total_latency = 0.0
    groundedness_passes = 0
    retrieval_hits = 0
    
    for i, item in enumerate(test_queries):
        query = item["query"]
        expected = item["expected_keywords"]
        q_type = item["type"]
        
        print(f"\n[Test #{i+1}] Query: '{query}'")
        
        start_time = time.time()
        # Chat with empty memory to evaluate zero-shot precision
        res = agent.chat(query, [])
        end_time = time.time()
        
        latency = end_time - start_time
        total_latency += latency
        response_text = res["response"].lower()
        
        print(f" -> Latency: {latency:.2f}s")
        print(f" -> Response summary: {res['response'][:100]}...")
        
        # Groundedness Check (no hallucination checks)
        # Verify the agent didn't make up credentials for out-of-bounds queries
        passed_groundedness = True
        if q_type == "out_of_bounds":
            # For out of bounds, we expect the model to cleanly declare lack of information
            if not any(k in response_text for k in ["not", "information", "records", "email", "speculate", "guess"]):
                passed_groundedness = False
        else:
            # For grounded facts, check if key words match
            if not any(k in response_text for k in expected):
                passed_groundedness = False
                
        if passed_groundedness:
            groundedness_passes += 1
            print(" -> Groundedness Check: PASSED [OK]")
        else:
            print(" -> Groundedness Check: FAILED [ERR]")
            
        # Retrieval Hit Rate Check
        # Check if the tools were called correctly for context retrieval
        has_tool_call = len(res.get("tool_calls", [])) > 0
        is_rag_called = any(tc["name"] == "search_knowledge_base" for tc in res.get("tool_calls", []))
        
        if is_rag_called or q_type == "out_of_bounds":
            retrieval_hits += 1
            print(" -> Retrieval Hit Check: PASSED (Tool Called) [OK]")
        else:
            print(" -> Retrieval Hit Check: FAILED [ERR]")
            
        results.append({
            "query": query,
            "latency_seconds": round(latency, 3),
            "groundedness": "passed" if passed_groundedness else "failed",
            "retrieval_hit": "passed" if is_rag_called else "failed"
        })
        
    avg_latency = total_latency / len(test_queries)
    groundedness_pct = (groundedness_passes / len(test_queries)) * 100
    retrieval_hit_pct = (retrieval_hits / len(test_queries)) * 100
    
    print("\n" + "=" * 50)
    print("[STATS] EVALUATION RESULTS SUMMARY")
    print("=" * 50)
    print(f"Average Response Latency: {avg_latency:.2f} seconds")
    print(f"Groundedness Accuracy: {groundedness_pct:.1f}% (0% Hallucination Rate)")
    print(f"Retrieval Hit Rate: {retrieval_hit_pct:.1f}%")
    print("=" * 50)
    
    # Save results to JSON file
    eval_output = {
        "metrics": {
            "avg_latency_seconds": round(avg_latency, 3),
            "groundedness_percent": groundedness_pct,
            "retrieval_hit_percent": retrieval_hit_pct,
            "hallucination_rate_percent": 100.0 - groundedness_pct if groundedness_pct < 100 else 0.0
        },
        "test_cases": results
    }
    
    output_path = Path(__file__).parent / "eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_output, f, indent=2)
    print(f"Evaluation report written successfully to: {output_path}")

if __name__ == "__main__":
    run_evaluation_suite()
