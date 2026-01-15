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
    
    # 1. Template Source
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(pkg_dir, "templates")
    
    if not os.path.exists(templates_dir):
        print("Warning: Templates directory not found. Using minimal fallback.")
        # Fallback logic could go here, or just fail. 
        # For now, let's assume templates exist if installed correctly.

    # 2. Iterate and Copy Components
    components = ["memory", "knowledge", "skills", "persona"]
    
    for comp in components:
        target_path = os.path.join(context_dir, comp)
        source_path = os.path.join(templates_dir, comp)
        
        if not os.path.exists(target_path):
            if os.path.exists(source_path) and os.path.isdir(source_path):
                shutil.copytree(source_path, target_path)
                print(f"  - Created {target_path} (from template)")
            else:
                os.makedirs(target_path, exist_ok=True)
                print(f"  - Created {target_path} (empty)")
                
                # Minimal Fallbacks for empty dirs
                if comp == "memory" and not os.path.exists(os.path.join(target_path, "memory.json")):
                    with open(os.path.join(target_path, "memory.json"), "w") as f:
                        f.write("{}")

                if comp == "knowledge" and not os.listdir(target_path):
                     with open(os.path.join(target_path, "README.txt"), "w") as f:
                        f.write("Add your knowledge base .txt files here.\n")
        else:
            print(f"  - {target_path} already exists. Skipping.")
            
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
