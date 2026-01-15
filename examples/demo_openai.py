import os
import sys

# Ensure we can import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ada_agent import Agent, OpenAICompatibleProvider

from dotenv import load_dotenv

def main():
    load_dotenv()
    print("--- Simple RAG Demo with Context ---")
    
    # 1. Setup Provider (OpenAI)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY in .env")
        return

    # base_url is optional for OpenAI (defaults to None -> official endpoint)
    model_name = "gpt-4o"
    
    provider = OpenAICompatibleProvider(
        api_key=api_key, 
        base_url=None, 
        model_name=model_name
    )
    
    # 3. Initialize Agent
    # The agent will automatically find 'context' in the current directory or create it.
    print("Initialize Agent (auto-context)...")
    agent = Agent(provider=provider, verbose=True)
    
    # 4. Ask a question that requires RAG
    # Data: "The capital of Mars is Utopia Planitia."
    question = "What is the capital of Mars in this universe?"
    print(f"\nUser: {question}")
    
    response = agent.chat(question)
    
    print(f"\nAgent: {response}")

if __name__ == "__main__":
    main()
