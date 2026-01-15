import subprocess
import os
import sys
import json

def run_command(command: str) -> str:
    """
    Executes a shell command and returns the output.
    WARNING: This tool allows executing arbitrary shell commands.
    """
    try:
        # Check for venv and update PATH to prioritize it
        env = os.environ.copy()
        
        # Use the current python interpreter's directory to ensure we stay in the same environment
        current_python_dir = os.path.dirname(sys.executable)
        env["PATH"] = f"{current_python_dir}{os.pathsep}{env.get('PATH', '')}"
        
        # Also set VIRTUAL_ENV legacy variable if we are in a venv
        if sys.prefix != sys.base_prefix:
             env["VIRTUAL_ENV"] = sys.prefix
        
        # Using shell=True to allow complex commands
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60,
            env=env
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error (Exit Code {result.returncode}):\n{result.stderr}"
    except Exception as e:
        return f"Execution Error: {str(e)}"

def read_file(path: str) -> str:
    """
    Reads the content of a file.
    """
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' not found."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Read Error: {str(e)}"

def list_files(path: str = ".") -> str:
    """
    Lists files in a directory.
    """
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"List Error: {str(e)}"

# Tool Definitions for OpenAI API
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command. Use this to run scripts, install packages, or perform system operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command line to execute (e.g., 'python skills/my_skill/script.py')"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Use this to inspect code, logs, or data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to read."
                    }
                },
                "required": ["path"]
            }
        }
    },
     {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory. Use this to discover available scripts or files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list (defaults to current directory).",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    }
]

# Mapping for execution
AVAILABLE_TOOLS = {
    "run_command": run_command,
    "read_file": read_file,
    "list_files": list_files
}
