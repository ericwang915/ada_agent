import os
import shutil

def init(project_path="."):
    """
    Initializes a new ADA Agent project by creating a 'context' directory
    with the necessary structure (memory, knowledge, skills) and sample files.
    """
    application_dir = os.path.abspath(project_path)
    context_dir = os.path.join(application_dir, "context")
    
    print(f"Initializing ADA Agent in application folder: {application_dir}")
    
    # 1. Create Directories
    components = ["memory", "knowledge", "skills", "persona"]
    for comp in components:
        comp_path = os.path.join(context_dir, comp)
        os.makedirs(comp_path, exist_ok=True)
        print(f"  - Created {comp_path}")
        
    # 2. Add Sample Files
    
    # Knowledge
    knowledge_readme = os.path.join(context_dir, "knowledge", "README.txt")
    if not os.path.exists(knowledge_readme):
        with open(knowledge_readme, "w") as f:
            f.write("Add your .txt files here to be indexed by the RAG system.\n")
            f.write("\nExample:\nThe capital of Mars is Utopia Planitia.\n")
            
    # Persona
    persona_file = os.path.join(context_dir, "persona", "default.md")
    if not os.path.exists(persona_file):
        with open(persona_file, "w") as f:
            f.write("You are a helpful and friendly assistant.\n")
            f.write("You like to use emojis in your responses. 🤖\n")

    # Memory (Optional initial memory)
    memory_file = os.path.join(context_dir, "memory", "memory.json")
    if not os.path.exists(memory_file):
        with open(memory_file, "w") as f:
            f.write("{}") # Empty JSON object
            
    # Skills
    # Try to copy from examples/context/skills if available (local dev mode)
    # This path is relative to ada_agent/init.py -> ../examples/context/skills
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(pkg_dir)
    examples_skills_dir = os.path.join(repo_root, "examples", "context", "skills")
    
    target_skills_dir = os.path.join(context_dir, "skills")
    
    if os.path.exists(examples_skills_dir) and os.path.isdir(examples_skills_dir):
        print(f"  - Copying example skills from {examples_skills_dir}...")
        try:
            # Iterate and copy each category/skill to avoid blowing away existing directory if any
            for item in os.listdir(examples_skills_dir):
                s = os.path.join(examples_skills_dir, item)
                d = os.path.join(target_skills_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        print(f"    - Skipping {item} (already exists)")
                    else:
                        shutil.copytree(s, d)
                        print(f"    - Copied {item}")
        except Exception as e:
            print(f"    - Error copying skills: {e}")
            
    # Always ensure at least hello_world exists if nothing else was copied
    # (Or just add it anyway as a demo of how to write one)
    skill_dir = os.path.join(target_skills_dir, "hello_world")
    if not os.path.exists(skill_dir):
        os.makedirs(skill_dir, exist_ok=True)
        
        skill_md = os.path.join(skill_dir, "SKILL.md")
        with open(skill_md, "w") as f:
            f.write("""---
name: hello_world
description: A simple skill to say hello.
---

# Hello World

Instructions:
1. Run the python script `hello.py` to say hello to the user.
""")

        skill_py = os.path.join(skill_dir, "hello.py")
        with open(skill_py, "w") as f:
            f.write("print('Hello from your custom skill!')\\n")
    else:
         print("  - hello_world skill already exists")
            
    # Env File
    env_file = os.path.join(application_dir, ".env")
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("# ADA Agent Configuration\n")
            f.write("# -----------------------\n\n")
            f.write("# LLM Provider Configuration\n")
            f.write("# Uncomment and fill in the key for your chosen provider\n\n")
            f.write("# OpenAI\n")
            f.write("# OPENAI_API_KEY=sk-your-openai-key-here\n\n")
            f.write("# DeepSeek\n")
            f.write("DEEPSEEK_API_KEY=sk-your-deepseek-key-here\n\n")
            f.write("# Anthropic (Claude)\n")
            f.write("# ANTHROPIC_API_KEY=sk-your-anthropic-key-here\n\n")
            f.write("# Google Gemini\n")
            f.write("# GEMINI_API_KEY=your-gemini-key-here\n")
        print(f"  - Created {env_file} (Please edit this file to add your API keys)")

    print("\nInitialization complete! You can now start your agent with this context.")
    print("Example usage:\n")
    print("1. Edit .env to set your API Key.")
    print("2. Run your agent script:\n")
    print("from ada_agent import Agent")
    print("from dotenv import load_dotenv; load_dotenv()")
    print("agent = Agent(..., knowledge_path='./context/knowledge', memory_path='./context/memory/memory.json', skills_dirs=['./context/skills'])")
