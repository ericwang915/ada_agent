# ADA: Python LLM Agent with Customizable Skills, Memory, Knowledge RAG & Persona

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**ADA** is a lightweight, provider-agnostic framework for building AI agents with **customizable skills**, **persistent memory**, **knowledge RAG**, and **personas**. Designed for simplicity and extensibility, ADA allows you to create agents that learn, remember, and act in local environments.

---

## 🚀 Features

- **🧠 Provider Agnostic**: Seamlessly switch between **DeepSeek**, **Gemini**, **Grok**, and **Claude**.
- **📚 Dynamic Skill System**: Load tools and "skills" on the fly based on context.
- **💾 Persistent Memory**: Long-term memory management using JSON-based storage (upgradable to Vector DB).
- **🛡️ Sandbox Ready**: Primitive tools (`run_command`, `read_file`) designed for safe execution environments.
- **🔌 Extensible Architecture**: Clean adapter patterns for LLMs make adding new providers trivial.

## 📦 Installation

### Option 1: Install via Pip (Recommended)
```bash
pip install git+https://github.com/ericwang915/ada_agent.git
```

### Option 2: Clone for Development
1. **Clone the Repository**
   ```bash
   git clone https://github.com/ericwang915/ada_agent.git
   cd ada_agent
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e .
   ```

## Examples

The `examples/` directory contains demo scripts for different LLM providers:

*   **DeepSeek**: `examples/demo_deepseek.py`
*   **OpenAI**: `examples/demo_openai.py`
*   **Google Gemini**: `examples/demo_gemini.py`
*   **Grok (xAI)**: `examples/demo_grok.py`

### Running a Demo

1.  Make sure you have set the appropriate API key in your `.env` file (created automatically by the agent or manually).
2.  Run the desired script:

```bash
# Example for DeepSeek
python examples/demo_deepseek.py

# Example for OpenAI
python examples/demo_openai.py
```

The demo scripts will automatically initialize a default `context` (skills, memory, knowledge) in your current directory if one doesn't exist.

## 🛠️ Configuration

When you first run the agent (or one of the demo scripts), it will automatically create a `.env` file in your current directory if one doesn't exist.

Open `.env` and fill in your API key:

```ini
# ADA Agent Configuration
# -----------------------

# LLM Provider Configuration
# Uncomment and fill in the key for your chosen provider

# OpenAI
# OPENAI_API_KEY=sk-your-openai-key-here

# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# Google Gemini
# GEMINI_API_KEY=your-gemini-key-here
```

## ⚡ Quick Start

Start the ADA generic agent:

```bash
ada
```

### Example Interaction

```text
You: Can you check the disk usage of my home directory?
ADA: I'll check that for you.
[Executing: df -h /Users/username]
ADA: Your home directory is using 45% of available space.
```

## 💻 Library Usage

You can use ADA as a library in your own Python projects, allowing for **custom memory**, **skills**, **knowledge base**, and **persona**.

```python
from ada_agent import Agent, OpenAICompatibleProvider
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Setup Provider
provider = OpenAICompatibleProvider(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 2. Initialize Agent
# The agent will automatically use or create a './context' folder in the current directory.
# You don't need to manually create folders or pass paths unless you want to customize them.
agent = Agent(provider=provider, verbose=True)

# 3. Chat
response = agent.chat("What can you do?")
print(response)
```

## 🎬 Demos

Check the `examples/` directory for ready-to-run scripts:

1.  **Full Demo**: `examples/demo.py`
    *   Demonstrates RAG (Knowledge), Custom Memory, Skills, and Persona configuration.

## 🧩 Architecture

```mermaid
graph TD
    User[User Input] --> Main[main.py]
    Main --> Agent[Core Agent]
    Agent --> LLM[LLM Adapter]
    Agent --> Memory[Memory Manager]
    Agent --> Skills[Skill Registry]
    
    subgraph Providers
        LLM --> DeepSeek
        LLM --> Gemini
        LLM --> Grok
        LLM --> Claude
    end
    
    subgraph Capabilities
        Skills --> Math
        Skills --> System
        Skills --> Filesystem
    end
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Built with ❤️ by the Open Source Community*
