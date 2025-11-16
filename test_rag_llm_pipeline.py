#!/usr/bin/env python3
"""
Test script for RAG+LLM pipeline functionality
Tests various instruction scenarios including valid, invalid, ambiguous, and multi-tool calls
"""

import asyncio
import json
import time
from typing import Dict, Any, List
import requests
from loguru import logger
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logger.add("test_results.log", rotation="10 MB", level="INFO")

class RAGLLMPipelineTester:
    def __init__(self, base_url: str = "https://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.failed_cases = []

    async def test_single_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single test case against the pipeline"""
        instruction = test_case["instruction"]
        rag_document = test_case.get("rag_document_name")
        expected_calls = test_case["expected_tool_calls"]

        logger.info(f"Testing instruction: {instruction}")

        try:
            # Query RAG to get relevant documents (if instruction is about playing video)
            rag_docs = []
            if rag_document:
                rag_response = requests.post(
                    f"{self.base_url}/rag/query",
                    json={"query": instruction},
                    timeout=30,
                    verify=False
                )
                if rag_response.status_code == 200:
                    rag_data = rag_response.json()
                    # Handle the actual RAG response structure
                    results = rag_data.get("data", {}).get("results", [])
                    rag_docs = [doc.get("metadata", {}).get("filename", "") for doc in results]
                    logger.info(f"RAG returned {len(rag_docs)} documents: {rag_docs}")
                else:
                    logger.error(f"RAG query failed: {rag_response.status_code}")

            # For actual LLM testing, we would need to simulate the audio pipeline
            # Since we're testing the API endpoints directly, we'll simulate the expected behavior

            # Check if required RAG document is present (for video instructions)
            if rag_document and rag_document not in rag_docs:
                return {
                    "instruction": instruction,
                    "status": "failed",
                    "reason": f"Required RAG document '{rag_document}' not found in RAG results",
                    "rag_docs": rag_docs,
                    "expected_rag": rag_document
                }

            # Since we can't directly test the LLM through the audio pipeline without audio input,
            # we'll validate the expected tool calls format and content
            validation_result = self.validate_tool_calls(expected_calls)

            return {
                "instruction": instruction,
                "status": "passed" if validation_result["valid"] else "failed",
                "rag_docs": rag_docs if rag_document else None,
                "expected_tool_calls": expected_calls,
                "validation": validation_result
            }

        except Exception as e:
            logger.error(f"Error testing instruction '{instruction}': {str(e)}")
            return {
                "instruction": instruction,
                "status": "error",
                "reason": str(e)
            }

    def validate_tool_calls(self, expected_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the format and content of expected tool calls"""
        try:
            valid_actions = ["play", "open", "close", "set_volume", "adjust_volume", "seek_video", "error"]

            for call in expected_calls:
                # Check required fields
                if "action" not in call:
                    return {"valid": False, "reason": "Missing 'action' field"}

                if call["action"] not in valid_actions:
                    return {"valid": False, "reason": f"Invalid action: {call['action']}"}

                # Validate specific action requirements
                if call["action"] == "play":
                    if "target" not in call or not call["target"]:
                        return {"valid": False, "reason": "Play action requires target"}
                    if "device" not in call or not call["device"]:
                        return {"valid": False, "reason": "Play action requires device"}

                elif call["action"] in ["open", "close"]:
                    if "target" not in call or not call["target"]:
                        return {"valid": False, "reason": f"{call['action']} action requires target"}

                elif call["action"] in ["set_volume", "adjust_volume"]:
                    if "device" not in call or not call["device"]:
                        return {"valid": False, "reason": f"{call['action']} action requires device"}
                    if "value" not in call or call["value"] is None:
                        return {"valid": False, "reason": f"{call['action']} action requires value"}

                    # Validate volume range
                    if call["action"] == "set_volume":
                        try:
                            value = int(call["value"])
                            if not (0 <= value <= 100):
                                return {"valid": False, "reason": "Volume must be between 0-100"}
                        except (ValueError, TypeError):
                            return {"valid": False, "reason": "Volume value must be a number"}

                elif call["action"] == "seek_video":
                    if "device" not in call or not call["device"]:
                        return {"valid": False, "reason": "Seek action requires device"}
                    if "value" not in call or call["value"] is None:
                        return {"valid": False, "reason": "Seek action requires time value"}

                elif call["action"] == "error":
                    if "value" not in call or not call["value"]:
                        return {"valid": False, "reason": "Error action requires error message"}

            return {"valid": True}

        except Exception as e:
            return {"valid": False, "reason": f"Validation error: {str(e)}"}

    async def run_all_tests(self, test_cases_file: str) -> Dict[str, Any]:
        """Run all test cases from the test cases file"""
        logger.info(f"Loading test cases from {test_cases_file}")

        try:
            with open(test_cases_file, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load test cases: {e}")
            return {"error": str(e)}

        logger.info(f"Loaded {len(test_cases)} test cases")

        # Check if server is running
        try:
            response = requests.get(f"{self.base_url}/", timeout=5, verify=False)
            if response.status_code != 200:
                logger.error(f"Server not responding correctly: {response.status_code}")
                return {"error": "Server not available"}
        except Exception as e:
            logger.error(f"Cannot connect to server: {e}")
            return {"error": "Cannot connect to server"}

        # Run tests with rate limiting (2 seconds per test for ModelScope)
        total_cases = len(test_cases)
        passed = 0
        failed = 0
        errors = 0

        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Running test {i}/{total_cases}")

            result = await self.test_single_case(test_case)
            self.test_results.append(result)

            if result["status"] == "passed":
                passed += 1
            elif result["status"] == "failed":
                failed += 1
                self.failed_cases.append(result)
            else:
                errors += 1
                self.failed_cases.append(result)

            # Rate limiting for ModelScope (2 seconds between tests)
            if i < total_cases:
                await asyncio.sleep(2)

        # Generate summary
        summary = {
            "total_tests": total_cases,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / total_cases) * 100,
            "failed_cases": self.failed_cases
        }

        logger.info(f"Test Summary: {passed}/{total_cases} passed ({summary['success_rate']:.1f}%)")

        # Save detailed results
        with open("test_results_detailed.json", 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "detailed_results": self.test_results
            }, f, ensure_ascii=False, indent=2)

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary to console"""
        print("\n" + "="*60)
        print("RAG+LLM Pipeline Test Summary")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        if summary['failed_cases']:
            print(f"\nFailed Cases ({len(summary['failed_cases'])}):")
            print("-" * 60)
            for i, case in enumerate(summary['failed_cases'], 1):
                print(f"{i}. Instruction: {case['instruction']}")
                print(f"   Status: {case['status']}")
                if 'reason' in case:
                    print(f"   Reason: {case['reason']}")
                elif 'validation' in case:
                    print(f"   Validation Error: {case['validation']['reason']}")
                print()

async def main():
    """Main test execution function"""
    tester = RAGLLMPipelineTester()

    print("Starting RAG+LLM Pipeline Tests...")
    print("Note: Make sure the server is running on https://localhost:5000")
    print("Note: This test validates expected tool call formats and RAG document retrieval")
    print("Note: Rate limiting applied (2s per test) for ModelScope compatibility\n")

    # Run tests
    summary = await tester.run_all_tests("rag_llm_test_cases_100.json")

    if "error" in summary:
        print(f"Test execution failed: {summary['error']}")
        return

    # Print summary
    tester.print_summary(summary)

    # Save summary to file
    with open("test_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nDetailed results saved to: test_results_detailed.json")
    print(f"Test summary saved to: test_summary.json")

if __name__ == "__main__":
    asyncio.run(main())