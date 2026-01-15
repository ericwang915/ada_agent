import os
import json
from openai import OpenAI
from .tools import TOOLS_SCHEMA, AVAILABLE_TOOLS, run_command, read_file, list_files
from .skill_loader import SkillRegistry, load_skill_by_name, search_skills, list_skills_in_category
from .memory.manager import MemoryManager
from .knowledge.rag import SimpleRAG
from .llm.base import LLMProvider

class Agent:
    def __init__(self, provider: LLMProvider, memory_path: str = None, skills_dirs: list[str] = None, knowledge_path: str = None, persona_path: str = None, verbose=False, show_full_context=False, max_chat_history=10):
        # 1. Automatic Context Initialization (Simplification)
        # If no paths are provided, default to ./context in the current working directory.
        if memory_path is None and skills_dirs is None and knowledge_path is None and persona_path is None:
            cwd = os.getcwd()
            context_dir = os.path.join(cwd, "context")
            
            # Auto-init if missing
            if not os.path.exists(context_dir):
                if verbose:
                    print(f"[Agent] No context found. Initializing default context in {context_dir}...")
                try:
                    # Local import to avoid circular dependency (ada_agent -> core.agent -> ada_agent)
                    from ...init import init
                    init(cwd)
                except ImportError:
                    # Fallback if relative import fails or structure is different
                    try:
                        from ada_agent.init import init
                        init(cwd)
                    except ImportError:
                         print("[Agent] Warning: Could not auto-initialize context. Please run 'ada_agent.init()' manually.")
            
            # Set defaults
            if verbose: print(f"[Agent] Using default context at {context_dir}")
            
            memory_path = os.path.join(context_dir, "memory", "memory.json")
            knowledge_path = os.path.join(context_dir, "knowledge")
            skills_dirs = [os.path.join(context_dir, "skills")]
            persona_path = os.path.join(context_dir, "persona")

        self.provider = provider
        self.messages = []
        self.verbose = verbose
        self.show_full_context = show_full_context
        self.max_chat_history = max_chat_history
        # We start with NO specific skills loaded, only the directory info
        self.loaded_skill_names = set()
        self.pending_injections = [] # Buffer for system messages during tool loops
        
        # Initialize Memory
        # If memory_path is provided, it overtakes default env var
        mem_path = memory_path or os.getenv("ADA_MEMORY_PATH")
        self.memory = MemoryManager(mem_path)

        # Initialize Simple RAG
        # If knowledge_path is provided, it overtakes default env var
        self.rag = None
        if knowledge_path and os.path.exists(knowledge_path):
            self.rag = SimpleRAG(knowledge_path)
            if self.verbose:
                print(f"[DEBUG] RAG initialized with knowledge path: {knowledge_path}")
        
        # Initialize Skills
        # We rely on the user to provide skills_dirs (e.g. from init or manual setup)
        self.skills_dirs = []
        if skills_dirs:
            if isinstance(skills_dirs, str):
                 self.skills_dirs.append(skills_dirs)
            else:
                 self.skills_dirs.extend(skills_dirs)
                 
        self.persona_instruction = ""
        if persona_path and os.path.exists(persona_path):
            if os.path.isfile(persona_path):
                 with open(persona_path, "r", encoding="utf-8") as f:
                     self.persona_instruction = f.read()
            elif os.path.isdir(persona_path):
                 # Load all .md or .txt files
                 for filename in sorted(os.listdir(persona_path)):
                     if filename.lower().endswith(('.md', '.txt')):
                         with open(os.path.join(persona_path, filename), "r", encoding="utf-8") as f:
                             self.persona_instruction += f"\n\n--- Persona: {filename} ---\n" + f.read()
            
            if self.verbose:
                print(f"[DEBUG] Loaded persona from {persona_path} (Length: {len(self.persona_instruction)})")

        self._init_system_prompt()

    def _init_system_prompt(self):
        # Use provided skills_dirs
        registry = SkillRegistry(skills_dirs=self.skills_dirs)
        categories_meta = registry.get_categories()
        
        # Build category list string with descriptions
        cat_str_list = []
        for c in categories_meta:
            cat_str_list.append(f"- {c.name}: {c.description}")
        categories_display = "\n   ".join(cat_str_list)
        
        system_msg = f"""You are a helpful AI assistant.
{self.persona_instruction}
You operate in a potentially sandboxed environment where you can execute code.

### Tool Capabilities
1. **Primitive Tools**: `run_command`, `read_file`, `list_files`
2. **Skill Discovery**:
   - Your skills are organized by CATEGORY.
   - Available Categories:
   {categories_display}
   - To see skills in a category, use: `list_skills(category="name")`
   - To using a skill, you MUST enable it first: `enable_skill(skill_name="name")`

### Workflow
1. User asks a question.
2. If you need a specific capability (e.g. Math), check the 'Math' category with `list_skills`.
3. Read the descriptions. If one matches, `enable_skill` for it.
4. Once enabled, the system will inject the specific instructions (which often tell you to run a python script).
5. Follow those instructions.

### Memory
You have a long-term memory. 
- **AGGRESSIVE MEMORY UPDATE**: You must proactively save **ALL** user profile details, preferences, and key facts using `remember`. Do not wait for explicit instructions. If the user mentions their profession, hobbies, name, or preferences, store it immediately.
- Use `recall(query="ignored")` to retrieve ALL stored memories. The query parameter is currently ignored, so you will see everything.
- ALWAYS check your memory (`recall`) if the user asks something that might be stored from a previous session.

Always verify the output of your commands.

### Response Guidelines
- Answer the user's question directly and concisely.
- Do NOT mention what skills or tools you are using or have available, unless the user explicitly asks about them.
- Do NOT list other things you can do at the end of your response.
"""
        self.messages.append({"role": "system", "content": system_msg})
        if self.verbose:
            print("\n[DEBUG] Initial System Prompt:")
            print("-" * 40)
            print(system_msg)
            print("-" * 40 + "\n")

    def _prune_navigation_history(self):
        """
        Aggressively prunes history:
        1. Completely REMOVES 'list_skills' interaction pairs (Assistant call + Tool output) 
           if they were single-turn calls. This effectively 'folds' the discovery process.
        2. Minifies tool outputs for other discovery tools if they can't be removed.
        """
        messages_to_keep = []
        skip_indices = set()
        
        # 1. Identify pairs to remove
        for i, msg in enumerate(self.messages):
            if i in skip_indices:
                continue
                
            # Look for Assistant -> Tool pattern
            if msg.get('role') == 'assistant' and msg.get('tool_calls'):
                tool_calls = msg['tool_calls']
                
                # Check if this is a standalone 'list_skills' call
                if len(tool_calls) == 1:
                    first_call = tool_calls[0]
                    # Handle object or dict
                    fname = first_call['function']['name'] if isinstance(first_call, dict) else first_call.function.name
                    
                    if fname in ('list_skills', 'list_files', 'search_skills'):
                        # Check if next message is the corresponding tool output
                        if i + 1 < len(self.messages):
                            next_msg = self.messages[i+1]
                            if next_msg.get('role') == 'tool':
                                # Found a pair to remove!
                                skip_indices.add(i)
                                skip_indices.add(i+1)
                                if self.verbose:
                                    print(f"[DEBUG] Folding discovery step: Removed {fname} interaction.")
                                continue

        # 2. Rebuild message list (and apply content pruning to remainders)
        for i, msg in enumerate(self.messages):
            if i in skip_indices:
                continue
            
            # Fallback: Content Pruning for anything that survived (e.g. part of parallel calls)
            if msg.get('role') == 'tool':
                # We need to check function name again if disjoint
                # But simple heuristic: close substantial outputs
                if len(msg.get('content', '')) > 200:
                    # Double check if it's a discovery tool by content heuristics or ID mapping
                    # For simplicity/safety, we assume previous pruning logic was fine, 
                    # but since we are rebuilding, let's just leave it or specific check.
                    # Let's trust the 'Folding' is the main optimization.
                    pass 
            
            messages_to_keep.append(msg)
            
        self.messages = messages_to_keep

    def _enable_skill(self, skill_name):
        if skill_name in self.loaded_skill_names:
            return f"Skill '{skill_name}' is already enabled."
        
        skill = load_skill_by_name(skill_name, skills_dirs=self.skills_dirs)
        if not skill:
            return f"Error: Skill '{skill_name}' not found."
            
        # Inject Instructions
        injection = f"""
[SYSTEM UPDATE]
Skill Enabled: {skill.name}
Description: {skill.description}
Path: {skill.metadata.path}

### SKILL INSTRUCTIONS
{skill.instructions}
"""
        # Buffer this injection to avoid breaking tool call block
        self.pending_injections.append(injection)
        self.loaded_skill_names.add(skill_name)
        
        # Optimization: Remove previous discovery noise now that we succeeded
        self._prune_navigation_history()
        
        if self.verbose:
            print(f"[DEBUG] Buffered instructions for {skill_name}")
            
        return f"Skill '{skill_name}' enabled successfully. Instructions have been added to your context."

    def _get_pruned_messages(self):
        """
        Creates a optimized context window:
        1. Keeps ALL 'system' messages (Prompts + Skill Injections).
        2. Keeps only the last 'max_chat_history' of conversation messages.
        3. Ensures we don't cut off a tool call flow (orphaned tool outputs).
        """
        system_msgs = [m for m in self.messages if m.get('role') == 'system']
        chat_msgs = [m for m in self.messages if m.get('role') != 'system']
        
        if len(chat_msgs) > self.max_chat_history:
            # Simple slicing - take last N
            pruned_chat = chat_msgs[-self.max_chat_history:]
            
            # Safety check: Ensure the first message isn't a 'tool' output without its call
            # or an assistant message with tool_calls but we lost the response?
            # Actually, standard OpenAI flow: User -> Assistant(calls) -> Tool(results).
            # If we cut in the middle, we might break things.
            # Aggressive strategy: Only start with 'user' role if possible.
            
            while pruned_chat and pruned_chat[0].get('role') == 'tool':
                pruned_chat.pop(0)
            
            # Also if first is assistant with tool_calls, we are fine, provided we have the tool responses (which we should, as we take the tail).
            
            chat_msgs = pruned_chat
            
        return system_msgs + chat_msgs

    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        if self.verbose:
            print(f"[DEBUG] User Input: {user_input}")
        
        while True:
            try:
                # Use Pruned History for the actual API call
                messages_to_send = self._get_pruned_messages()

                # ... (schema definition code) ...
                
                current_tools = [
                    *TOOLS_SCHEMA,
                    {
                        "type": "function",
                        "function": {
                            "name": "list_skills",
                            "description": "List available skills in a category.",
                            "parameters": {
                                "type": "object",
                                "properties": {"category": {"type": "string"}},
                                "required": ["category"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "enable_skill",
                            "description": "Enable a specific skill (load its instructions).",
                            "parameters": {
                                "type": "object",
                                "properties": {"skill_name": {"type": "string"}},
                                "required": ["skill_name"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "remember",
                            "description": "Store a piece of information in long-term memory.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string", "description": "The topic or key to store under."},
                                    "content": {"type": "string", "description": "The information to store."}
                                },
                                "required": ["key", "content"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "recall",
                            "description": "Search long-term memory for information.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "The topic or keyword to search for."}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                ]
                
                # Dynamic Tool: Consult Knowledge Base (Only if RAG is active)
                if self.rag:
                    current_tools.append({
                        "type": "function",
                        "function": {
                            "name": "consult_knowledge_base",
                            "description": "Consult the knowledge base to answer questions using provided text files. Use this when the user asks about facts that might be in the knowledge base.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "The specific query to search for in the knowledge base."}
                                },
                                "required": ["query"]
                            }
                        }
                    })

                if self.show_full_context:
                    print("\n" + "="*80)
                    print(f" SENDING REQUEST TO LLM (Messages: {len(messages_to_send)} / Total History: {len(self.messages)})")
                    print("="*80)
                    print(json.dumps(messages_to_send, indent=2, ensure_ascii=False))
                    print("="*80 + "\n")

                response = self.provider.chat(
                    messages=messages_to_send,
                    tools=current_tools,
                    tool_choice="auto"
                )
                
                # ... (rest of loop) ...
                
                message = response.choices[0].message
                
                if not message.tool_calls:
                    if self.verbose:
                        print(f"[DEBUG] Final Response: {message.content}")
                    self.messages.append(message.model_dump())
                    return message.content
                
                # Append assistant message (convert to dict to be safe)
                self.messages.append(message.model_dump())
                
                # Execute tools
                self.pending_injections = [] # Reset pending injections for this turn
                
                for tool_call in message.tool_calls:
                    try:
                        func_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        
                        if self.verbose:
                            print(f"\n[DEBUG] Tool Call: {func_name} (ID: {tool_call.id})")
                            print(f"[DEBUG] Args: {args}")

                        result = ""
                        if func_name == "list_skills":
                            # Use helper with configured dir
                            skills = list_skills_in_category(args.get("category"), skills_dirs=self.skills_dirs)
                            result = json.dumps(skills, indent=2)
                        elif func_name == "search_skills":
                            results = search_skills(args.get("query"), skills_dirs=self.skills_dirs)
                            result = json.dumps(results, indent=2)
                        elif func_name == "enable_skill":
                            result = self._enable_skill(args.get("skill_name"))
                        elif func_name == "remember":
                            result = self.memory.remember(args.get("content"), args.get("key"))
                        elif func_name == "recall":
                            result = self.memory.recall(args.get("query"))
                        elif func_name == "consult_knowledge_base" and self.rag:
                             # Use RAG
                            hits = self.rag.retrieve(args.get("query"))
                            if hits:
                                result = "Found relevant info:\n"
                                for h in hits:
                                    result += f"- [{h['source']}]: {h['content']}\n"
                            else:
                                result = "No relevant information found in the knowledge base."
                        elif func_name in AVAILABLE_TOOLS:
                            result = AVAILABLE_TOOLS[func_name](**args)
                        else:
                            result = f"Error: Tool {func_name} not found."
                    except Exception as e:
                        result = f"Error executing tool {func_name}: {str(e)}"

                    if self.verbose:
                        # Truncate long output for debug
                        debug_output = str(result)
                        if len(debug_output) > 200:
                            debug_output = debug_output[:200] + "..."
                        print(f"[DEBUG] Tool Output: {debug_output}")

                    # Append tool result
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
                
                # Process any pending system injections (e.g. from enable_skill) AFTER valid tool block
                if self.pending_injections:
                    for injection in self.pending_injections:
                        self.messages.append({"role": "system", "content": injection})
                    self.pending_injections = []
            except Exception as e:
                 # If we crashed outside the inner tool loop but after appending assistant msg, we might still be in trouble.
                 # But the main risk was the tool execution itself.
                 print(f"CRITICAL AGENT ERROR: {e}") # Log it
                 return f"Error: {e}"
