#!/usr/bin/env python3
"""
RAG Performance Test Script
Tests accuracy and latency of the RAG system using natural language queries.
"""

import json
import time
import requests
import numpy as np
from typing import List, Dict, Any
from loguru import logger
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logger.add("rag_performance_test.log", rotation="10 MB", level="INFO")

class RAGPerformanceTester:
    def __init__(self, base_url: str = "https://localhost:5000"):
        self.base_url = base_url
        self.results = []

    def run_test(self, test_cases_file: str):
        """Run performance tests"""
        logger.info(f"Loading test cases from {test_cases_file}")
        
        try:
            with open(test_cases_file, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load test cases: {e}")
            return

        total_cases = len(test_cases)
        logger.info(f"Starting performance test with {total_cases} cases")

        latencies = []
        top1_hits = 0
        top3_hits = 0
        
        print(f"{'Query':<50} | {'Expected':<30} | {'Rank':<5} | {'Latency (ms)':<10} | {'Status'}")
        print("-" * 110)

        for i, case in enumerate(test_cases, 1):
            query = case["query"]
            expected = case["expected_video"]
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/rag/query",
                    json={"query": query},
                    timeout=30,
                    verify=False
                )
                latency = (time.time() - start_time) * 1000 # ms
                latencies.append(latency)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("data", {}).get("results", [])
                    retrieved_docs = [doc.get("metadata", {}).get("filename", "") for doc in results]
                    
                    # Check rank
                    rank = -1
                    if expected in retrieved_docs:
                        rank = retrieved_docs.index(expected) + 1
                    
                    if rank == 1:
                        top1_hits += 1
                    if rank > 0 and rank <= 3:
                        top3_hits += 1
                    
                    status = "PASS" if rank == 1 else ("WARN" if rank > 0 else "FAIL")
                    
                    print(f"{query[:47]:<50} | {expected[:27]:<30} | {rank:<5} | {latency:.2f}      | {status}")
                    
                    self.results.append({
                        "query": query,
                        "expected": expected,
                        "retrieved": retrieved_docs[:3],
                        "rank": rank,
                        "latency": latency,
                        "status": status
                    })
                else:
                    logger.error(f"Request failed: {response.status_code}")
                    print(f"{query[:47]:<50} | {expected[:27]:<30} | N/A   | {latency:.2f}      | ERROR")

            except Exception as e:
                logger.error(f"Error processing case: {e}")
                print(f"{query[:47]:<50} | {expected[:27]:<30} | N/A   | N/A        | ERROR")

        # Calculate statistics
        avg_latency = np.mean(latencies) if latencies else 0
        p95_latency = np.percentile(latencies, 95) if latencies else 0
        p99_latency = np.percentile(latencies, 99) if latencies else 0
        top1_accuracy = (top1_hits / total_cases) * 100
        top3_accuracy = (top3_hits / total_cases) * 100

        print("\n" + "="*60)
        print("RAG Performance Test Summary")
        print("="*60)
        print(f"Total Cases: {total_cases}")
        print(f"Top-1 Accuracy: {top1_accuracy:.1f}% ({top1_hits}/{total_cases})")
        print(f"Top-3 Accuracy: {top3_accuracy:.1f}% ({top3_hits}/{total_cases})")
        print(f"Average Latency: {avg_latency:.2f} ms")
        print(f"P95 Latency: {p95_latency:.2f} ms")
        print(f"P99 Latency: {p99_latency:.2f} ms")
        
        # Save detailed results
        output = {
            "summary": {
                "total_cases": total_cases,
                "top1_accuracy": top1_accuracy,
                "top3_accuracy": top3_accuracy,
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "p99_latency": p99_latency
            },
            "detailed_results": self.results
        }
        
        with open("rag_performance_results.json", 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"\nDetailed results saved to: rag_performance_results.json")

if __name__ == "__main__":
    tester = RAGPerformanceTester()
    tester.run_test("rag_performance_test_cases.json")
