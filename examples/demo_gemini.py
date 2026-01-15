import os
import sys

# Ensure we can import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ada_agent import Agent

def main():
    print("--- Simple RAG Demo with Context (Gemini) ---")
    
    # 1. Setup Provider (Gemini)
    api_key = os.getenv("GEMINI_API_KEY")

    model_name = "gemini-2.0-flash-exp" # or your preferred model
    
    from ada_agent.core.llm.gemini_client import GeminiProvider
    provider = GeminiProvider(
        api_key=api_key, 
        model_name=model_name
    )
    
    # 2. Initialize Agent
    # The agent will automatically find 'context' in the current directory or create it.
    print("Initialize Agent (auto-context)...")
    agent = Agent(provider=provider)
    
    # 3. Ask a question that requires RAG
    # Data: "The capital of Mars is Utopia Planitia."
    question = "What is the capital of Mars in this universe?"
    print(f"\nUser: {question}")
    
    response = agent.chat(question)
    
    print(f"\nAgent: {response}")

if __name__ == "__main__":
    main()
