import json
import statistics
from datetime import datetime

def compile_benchmark_results(benchmark_results, bench_data, num_runs_per_test, benchmark_name="Superface Specialist Benchmark"):
    """
    Compile benchmark results into a structured format with summary statistics.
    
    Args:
        benchmark_results: List of individual test results
        bench_data: Original benchmark test data
        num_runs_per_test: Number of runs per test case
        benchmark_name: Name of the benchmark
        
    Returns:
        Dictionary containing compiled results and statistics
    """
    # Compile final results
    final_results = {
        "timestamp": datetime.now().isoformat(),
        "benchmark_name": benchmark_name,
        "total_tests": len(bench_data),
        "successful_tests": sum(1 for r in benchmark_results if r['success']),
        "failed_tests": sum(1 for r in benchmark_results if not r['success']),
        "tool_calls_match_count": sum(1 for r in benchmark_results if r.get('tool_calls_match', False)),
        "success_rate": (sum(1 for r in benchmark_results if r['success']) / len(bench_data)) * 100,
        "tool_call_match_rate": (sum(1 for r in benchmark_results if r.get('tool_calls_match', False)) / len(bench_data)) * 100
    }

    # For JSON serialization, convert CrewOutput objects to strings
    serializable_results = []
    for r in benchmark_results:
        serializable_result = r.copy()
        if r['success'] and r['result'] is not None:
            serializable_result['result'] = str(r['result'])
        # Make sure actual_tool_calls is included
        if 'actual_tool_calls' not in serializable_result:
            serializable_result['actual_tool_calls'] = []
        serializable_results.append(serializable_result)

    # Update the final_results with serializable results
    final_results["results"] = serializable_results

    # Calculate additional summary statistics
    run_durations = [r['duration_seconds'] for r in benchmark_results]
    if run_durations:
        final_results["summary_stats"] = {
            "avg_test_duration": statistics.mean(run_durations),
            "min_test_duration": min(run_durations),
            "max_test_duration": max(run_durations),
            "std_dev_test_duration": statistics.stdev(run_durations) if len(run_durations) > 1 else 0,
            "total_benchmark_duration": sum(run_durations),
            "runs_per_test": num_runs_per_test
        }
        
        # Collect all mismatch reasons across tests
        all_mismatch_reasons = {}
        for result in benchmark_results:
            if 'stats' in result and 'mismatch_summary' in result['stats']:
                for reason, count in result['stats']['mismatch_summary'].items():
                    all_mismatch_reasons[reason] = all_mismatch_reasons.get(reason, 0) + count
        
        final_results["summary_stats"]["mismatch_reasons"] = all_mismatch_reasons
    
    return final_results

def save_benchmark_results(final_results, prefix="benchmark_results"):
    """
    Save benchmark results to a JSON file.
    
    Args:
        final_results: Dictionary containing benchmark results
        prefix: Prefix for the filename
        
    Returns:
        Path to the saved file
    """
    results_filename = f"./results/{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Ensure the results directory exists
    import os
    os.makedirs("./results", exist_ok=True)
    
    # Make sure success_rate and tool_call_match_rate are included
    if 'success_rate' not in final_results:
        final_results['success_rate'] = (final_results['successful_tests'] / final_results['total_tests']) * 100
    
    if 'tool_call_match_rate' not in final_results:
        final_results['tool_call_match_rate'] = (final_results['tool_calls_match_count'] / final_results['total_tests']) * 100
    
    with open(results_filename, "w") as f:
        json.dump(final_results, f, indent=2)
    
    return results_filename

def print_benchmark_summary(final_results):
    """
    Print a summary of benchmark results.
    
    Args:
        final_results: Dictionary containing benchmark results
    """
    print("\n=== Benchmark Summary ===")
    print(f"Total tests: {final_results['total_tests']}")
    print(f"Successful tests: {final_results['successful_tests']}")
    print(f"Failed tests: {final_results['failed_tests']}")
    print(f"Tests with matching tool calls: {final_results['tool_calls_match_count']}")
    print(f"Success rate: {final_results['success_rate']:.2f}%")
    print(f"Tool call match rate: {final_results['tool_call_match_rate']:.2f}%")
    
    if "summary_stats" in final_results:
        stats = final_results["summary_stats"]
        print(f"\nAverage test duration: {stats['avg_test_duration']:.2f} seconds")
        print(f"Total benchmark duration: {stats['total_benchmark_duration']:.2f} seconds")
        
        if "mismatch_reasons" in stats and stats["mismatch_reasons"]:
            print("\nMismatch reasons:")
            for reason, count in stats["mismatch_reasons"].items():
                print(f"- {reason} (occurred {count} times)") 