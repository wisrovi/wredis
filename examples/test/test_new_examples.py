"""Tests for new example scripts."""

import subprocess
import pathlib

EXAMPLES_ROOT = pathlib.Path(__file__).parent.parent

NEW_EXAMPLE_DIRS = [
    "sync/serializer",
    "sync/validation",
    "sync/retry",
    "sync/base_manager",
    "async/async_base",
    "sync/cache_metrics",
    "sync/exceptions",
]


def _get_example_files():
    """Get all example Python files from new directories."""
    files = []
    for d in NEW_EXAMPLE_DIRS:
        dir_path = EXAMPLES_ROOT / d
        if dir_path.exists():
            files.extend(sorted(dir_path.glob("*.py")))
    return files


class TestNewExamples:
    """Test that all new example scripts run successfully."""

    def test_example_files_exist(self):
        """Verify all example directories have files."""
        for d in NEW_EXAMPLE_DIRS:
            dir_path = EXAMPLES_ROOT / d
            assert dir_path.exists(), f"Directory missing: {d}"
            py_files = list(dir_path.glob("*.py"))
            assert len(py_files) >= 15, f"Expected 15+ examples in {d}, got {len(py_files)}"

    def test_readme_files_exist(self):
        """Verify each example directory has a README."""
        for d in NEW_EXAMPLE_DIRS:
            readme = EXAMPLES_ROOT / d / "README.md"
            assert readme.exists(), f"README missing in {d}"

    def test_all_examples_run(self):
        """Test that every example script executes without error."""
        for f in _get_example_files():
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, (
                f"Example {f.relative_to(EXAMPLES_ROOT)} failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

    def test_serializer_examples(self):
        """Test serializer examples specifically."""
        for f in sorted((EXAMPLES_ROOT / "sync/serializer").glob("*.py")):
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"{f.name} failed: {result.stderr}"

    def test_validation_examples(self):
        """Test validation examples specifically."""
        for f in sorted((EXAMPLES_ROOT / "sync/validation").glob("*.py")):
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"{f.name} failed: {result.stderr}"

    def test_retry_examples(self):
        """Test retry examples specifically."""
        for f in sorted((EXAMPLES_ROOT / "sync/retry").glob("*.py")):
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"{f.name} failed: {result.stderr}"

    def test_base_manager_examples(self):
        """Test base_manager examples specifically."""
        for f in sorted((EXAMPLES_ROOT / "sync/base_manager").glob("*.py")):
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"{f.name} failed: {result.stderr}"

    def test_async_base_examples(self):
        """Test async_base examples specifically."""
        for f in sorted((EXAMPLES_ROOT / "async/async_base").glob("*.py")):
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"{f.name} failed: {result.stderr}"

    def test_cache_metrics_examples(self):
        """Test cache_metrics examples specifically."""
        for f in sorted((EXAMPLES_ROOT / "sync/cache_metrics").glob("*.py")):
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"{f.name} failed: {result.stderr}"

    def test_exceptions_examples(self):
        """Test exceptions examples specifically."""
        for f in sorted((EXAMPLES_ROOT / "sync/exceptions").glob("*.py")):
            result = subprocess.run(
                ["python", str(f)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"{f.name} failed: {result.stderr}"
