
import os
import sys
import unittest
from unittest.mock import MagicMock

# Ensure we can import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ada_agent import Agent, OpenAICompatibleProvider

class TestMemoryPrompt(unittest.TestCase):
    def test_system_prompt_content(self):
        # Mock provider to avoid API calls
        provider = MagicMock()
        
        # Initialize Agent
        agent = Agent(provider=provider)
        
        # Get system prompt
        system_msg = agent.messages[0]['content']
        
        print("\n--- System Prompt Memory Section ---")
        # Extract memory section for verification
        if "### Memory" in system_msg:
             start = system_msg.find("### Memory")
             end = system_msg.find("###", start + 1)
             if end == -1: end = len(system_msg)
             print(system_msg[start:end])
        else:
            print("Memory section not found!")
        print("------------------------------------")
        
        # Verify keywords
        self.assertIn("AGGRESSIVE MEMORY UPDATE", system_msg)
        self.assertIn("proactively save", system_msg)
        self.assertIn("user profile details", system_msg)
        self.assertIn("retrieve ALL stored memories", system_msg)

if __name__ == "__main__":
    unittest.main()
