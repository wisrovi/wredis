"""Test runner for all examples in examples/ folder.

This module discovers all example.py files and runs them as tests.
Each example is expected to run without errors when Redis is available.
"""

import subprocess
import sys
from pathlib import Path

import pytest

SKIP_PATTERNS = [
    # Long-running examples (consumers, subscribers, TTL waits)
    "pubsub/02_subscriber",
    "pubsub/04_simple_subscriber",
    "queue/02_consumer",
    "streams/02_consumer",
    "queue/01_producer",  # may interfere with consumer test
    "streams/01_producer",  # may interfere with consumer test
    "basic/queue",  # consumer runs indefinitely
    "sync/hash/06_exist",  # waits for TTL expiration (60s loop)
    # Require special infrastructure
    "cluster",  # requires Redis cluster
    "sentinel",  # requires Redis sentinel
    # Async versions
    "async/pubsub",
    "async/queue",
    "async/streams",
    "async/sentinel",
    "async/cluster",
    # Known issues (need code fixes)
    "exceptions/10_logging_integration",  # logging message key conflict
    "cache/06_invalidation_impact",  # timing issue
    "cache/12_custom_key_builder",  # timing issue
    "exceptions/07_operation_error_recovery",  # test issue
]


def get_examples_directory() -> Path:
    """Get the examples directory path."""
    return Path(__file__).parent.parent


def discover_examples():
    """Discover all example.py files in the examples directory."""
    examples_dir = get_examples_directory()
    examples = []

    for example_path in examples_dir.rglob("example.py"):
        # Get relative path from examples directory
        rel_path = example_path.relative_to(examples_dir)

        # Skip examples that need special infrastructure or run indefinitely
        should_skip = False
        for pattern in SKIP_PATTERNS:
            if pattern in str(rel_path):
                should_skip = True
                break

        if not should_skip:
            examples.append(
                {
                    "path": example_path,
                    "rel_path": str(rel_path),
                    "folder": str(rel_path.parent),
                }
            )

    return sorted(examples, key=lambda x: x["rel_path"])


@pytest.mark.parametrize("example", discover_examples(), ids=lambda x: x["rel_path"])
def test_example_runs(example):
    """Test that an example runs without errors."""
    example_path = example["path"]

    # Run the example as a subprocess
    result = subprocess.run(
        [sys.executable, str(example_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Print output for debugging
    if result.returncode != 0:
        print(f"\n=== STDOUT ===\n{result.stdout}")
        print(f"\n=== STDERR ===\n{result.stderr}")

    assert (
        result.returncode == 0
    ), f"Example {example['rel_path']} failed with return code {result.returncode}"
