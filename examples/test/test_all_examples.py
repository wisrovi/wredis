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
    "pub_sub/consumer",
    "streams/consume",
    "queue/consumer",
    "pubsub/02_subscriber",
    "pubsub/04_simple_subscriber",
    "queue/02_consumer",
    "streams/02_consumer",
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
]


def get_examples_directory() -> Path:
    """Get the examples directory path."""
    return Path(__file__).parent.parent


def discover_examples():
    """Discover all .py files in the examples directory."""
    examples_dir = get_examples_directory()
    examples = []

    # Look for all .py files except those in the test/ directory or __init__.py
    for example_path in examples_dir.rglob("*.py"):
        if "examples/test/" in str(example_path) or example_path.name == "__init__.py":
            continue

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
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Print output for debugging
    if result.returncode != 0:
        print(f"\n=== STDOUT ===\n{result.stdout}")
        print(f"\n=== STDERR ===\n{result.stderr}")

    assert result.returncode == 0, f"Example {example['rel_path']} failed with return code {result.returncode}"
