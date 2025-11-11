#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone LLM Functional Test Script for China Mobile Smart Exhibition Hall

This script tests the LLM function calling capabilities using the generated test datasets.
It loads test instructions, processes them through the LLM handler, and compares results
against expected outputs to identify any failures.

Note: There is a 2-second delay between each test request to avoid overwhelming the LLM service
and to simulate more realistic usage patterns. This helps prevent rate limiting and ensures
stable testing conditions.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the src directory to Python path to import project modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.config.config import get_settings
from src.module.llm.modelscope_llm_handler import ModelScopeLLMHandler
from src.module.rag.rag_processor import RAGProcessor


def load_test_data() -> List[Dict[str, Any]]:
    """Load test data from both valid and invalid test files."""
    test_data = []

    # Load valid test data
    valid_file = project_root / "test_data_valid.json"
    if valid_file.exists():
        with open(valid_file, "r", encoding="utf-8") as f:
            valid_data = json.load(f)
            test_data.extend(valid_data)

    # Load invalid test data
    invalid_file = project_root / "test_data_invalid.json"
    if invalid_file.exists():
        with open(invalid_file, "r", encoding="utf-8") as f:
            invalid_data = json.load(f)
            test_data.extend(invalid_data)

    return test_data


def normalize_result(result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize result by ensuring consistent field types and sorting."""
    normalized = []
    for item in result:
        # Ensure all fields are present with proper types
        normalized_item = {
            "action": item.get("action"),
            "target": item.get("target"),
            "device": item.get("device"),
            "value": item.get("value")
        }
        normalized.append(normalized_item)
    return normalized


def compare_results(actual: List[Dict[str, Any]], expected: List[Dict[str, Any]]) -> bool:
    """Compare actual and expected results with proper normalization."""
    if len(actual) != len(expected):
        return False

    # Normalize both results
    norm_actual = normalize_result(actual)
    norm_expected = normalize_result(expected)

    # For simple cases (single item), direct comparison works
    if len(norm_actual) == 1:
        return norm_actual[0] == norm_expected[0]

    # For multiple items, we need to handle ordering
    # Since the system should maintain instruction order, we compare directly
    return norm_actual == norm_expected


async def run_llm_test(test_instruction: str, rag_processor: RAGProcessor, llm_handler: ModelScopeLLMHandler) -> List[Dict[str, Any]]:
    """Run a single test through the RAG+LLM pipeline and return parsed result."""
    try:
        # Retrieve relevant documents using RAG
        retrieved_docs = await rag_processor.retrieve_context(test_instruction)

        # Get response from LLM handler with retrieved documents
        response_str = await llm_handler.get_response(test_instruction, retrieved_docs)

        # Parse the JSON response
        response_data = json.loads(response_str)

        # Handle error responses - they should still be in the expected format
        if isinstance(response_data, list):
            return response_data
        else:
            # Unexpected format
            return [{"action": "error", "reason": "unexpected_format", "target": None, "device": None, "value": None}]

    except json.JSONDecodeError:
        # Invalid JSON response
        return [{"action": "error", "reason": "invalid_json", "target": None, "device": None, "value": None}]
    except Exception as e:
        # Other errors
        return [{"action": "error", "reason": "exception", "target": None, "device": None, "value": None, "message": str(e)}]


async def main():
    """Main test execution function."""
    print("Starting LLM Functional Tests for China Mobile Smart Exhibition Hall")
    print("=" * 80)

    # Load test data
    test_data = load_test_data()
    if not test_data:
        print("ERROR: No test data found! Please ensure test_data_valid.json and test_data_invalid.json exist.")
        return 1

    print(f"Loaded {len(test_data)} test cases")

    # Initialize settings, RAG processor, and LLM handler
    try:
        settings = get_settings()

        # Initialize RAG processor
        print("Initializing RAG processor...")
        rag_processor = RAGProcessor(settings.rag)
        await rag_processor.initialize()
        print("RAG processor initialized successfully")

        # Initialize LLM handler
        llm_handler = ModelScopeLLMHandler(settings.llm)
        print("Initializing LLM handler...")
        await llm_handler.initialize()
        print("LLM handler initialized successfully")

    except Exception as e:
        print(f"Failed to initialize components: {e}")
        return 1

    # Run tests
    passed_tests = 0
    failed_tests = []

    for i, test_case in enumerate(test_data, 1):
        instruction = test_case["instruction"]
        expected = test_case["expected"]

        print(f"\nTest {i}/{len(test_data)}: {instruction}")

        try:
            # Run the test through RAG+LLM pipeline
            actual_result = await run_llm_test(instruction, rag_processor, llm_handler)

            # Compare results
            if compare_results(actual_result, expected):
                print("PASSED")
                passed_tests += 1
            else:
                print("FAILED")
                failed_tests.append({
                    "instruction": instruction,
                    "expected": expected,
                    "actual": actual_result
                })
                print(f"   Expected: {json.dumps(expected, ensure_ascii=False, indent=4)}")
                print(f"   Actual:   {json.dumps(actual_result, ensure_ascii=False, indent=4)}")

            # Add 2-second delay between requests to avoid overwhelming the LLM service
            await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed_tests.append({
                "instruction": instruction,
                "expected": expected,
                "actual": f"Exception: {str(e)}"
            })

    # Print summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_data)}")
    print(f"Passed:      {passed_tests}")
    print(f"Failed:      {len(failed_tests)}")
    print(f"Success rate: {(passed_tests / len(test_data) * 100):.1f}%")

    if failed_tests:
        print(f"\nFAILED TESTS DETAILS:")
        print("-" * 50)
        for i, failed in enumerate(failed_tests, 1):
            print(f"\nFailure {i}:")
            print(f"   Instruction: {failed['instruction']}")
            print(f"   Expected: {json.dumps(failed['expected'], ensure_ascii=False)}")
            print(f"   Actual:   {json.dumps(failed['actual'], ensure_ascii=False) if isinstance(failed['actual'], list) else failed['actual']}")

    print("\n" + "=" * 80)

    # Return exit code (0 for success, 1 for failures)
    return 0 if len(failed_tests) == 0 else 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)