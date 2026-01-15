import os
import sys

# Ensure we can import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ada_agent import Agent, OpenAICompatibleProvider

def main():
    print("--- Simple RAG Demo with Context (Grok) ---")
    
    # 1. Setup Provider (Grok / xAI)
    api_key = os.getenv("XAI_API_KEY")

    base_url = "https://api.x.ai/v1"
    model_name = "grok-beta" # or grok-2-vision-1212 etc.
    
    provider = OpenAICompatibleProvider(
        api_key=api_key, 
        base_url=base_url,
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
