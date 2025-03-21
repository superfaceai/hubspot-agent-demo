import os
from dotenv import load_dotenv

def setup_benchmark_environment(specialist_id: str = "hubspot"):
    """
    Set up the environment for running benchmarks.
    Returns a dictionary with the configuration.
    """
    # Load environment variables
    load_dotenv(override=True)
    
    # Get benchmark configuration
    config = {
        "user_id": os.getenv("SUPERFACE_BENCHMARK_USER_ID", "benchmark_test"),
        "runs_per_test": int(os.getenv("BENCHMARK_RUNS_PER_TEST", 3)),
        "model": os.getenv("BENCHMARK_MODEL", "gpt-4o"),
        "specialist_id": specialist_id,
        "superface_api_key": os.getenv("SUPERFACE_API_KEY")
    }
    
    # Validate required environment variables
    required_vars = [
        "SUPERFACE_API_KEY",
        "SUPERFACE_BENCHMARK_USER_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return config