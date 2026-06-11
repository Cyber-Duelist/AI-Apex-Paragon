import os
import subprocess

def read_file(filepath: str) -> str:
    """Read the contents of a file in the mock_repo."""
    full_path = os.path.join(os.path.dirname(__file__), "mock_repo", filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Overwrite a file in the mock_repo with new content."""
    full_path = os.path.join(os.path.dirname(__file__), "mock_repo", filepath)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def run_tests() -> str:
    """Run pytest in the mock_repo and return the output logs."""
    repo_path = os.path.join(os.path.dirname(__file__), "mock_repo")
    import sys
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_calculator.py", "-v"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        # Return both stdout and stderr for full visibility
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"Failed to execute tests: {str(e)}"

# Define schemas for Groq to understand the tools
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a source code file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Name of the file to read (e.g., 'calculator.py')"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite a file with new code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Name of the file to write to"},
                    "content": {"type": "string", "description": "The full code content to write to the file"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run the automated test suite to see if the code is passing.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

AVAILABLE_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_tests": run_tests
}
