import os
from .utils import parse_frontmatter

class CategoryMetadata:
    """Level 1: Category metadata."""
    def __init__(self, name, description, path):
        self.name = name
        self.description = description
        self.path = path

class SkillMetadata:
    """Level 1: Lightweight metadata always loaded."""
    def __init__(self, name, description, path, category):
        self.name = name
        self.description = description
        self.path = path
        self.category = category

class Skill:
    """Level 2: Heavyweight instructions loaded on demand."""
    def __init__(self, metadata: SkillMetadata, instructions: str):
        self.metadata = metadata
        self.instructions = instructions

    @property
    def name(self):
        return self.metadata.name

    @property
    def description(self):
        return self.metadata.description


class SkillRegistry:
    def __init__(self, skills_dirs: list[str] = None):
        self.skills_dirs = []
        
        # Always add default if not explicitly excluded? 
        # Actually user might want ONLY custom. 
        # But for this task "fallback... but can append", I'll assume we want flexibility.
        # Let's just take the list. The Agent will decide what to pass.
        
        if skills_dirs:
             self.skills_dirs.extend(skills_dirs)
        
        # If empty, add default? Or maybe Agent handles default.
        # Let's make Registry dumb: just holds dirs.
        # But we need to calculate default if nothing passed?
        if not self.skills_dirs:
             # No default skills dir anymore
             pass

    def get_categories(self) -> list[CategoryMetadata]:
        """Returns a list of CategoryMetadata objects."""
        categories = []
        seen_categories = set()
        
        for s_dir in self.skills_dirs:
            if not os.path.exists(s_dir):
                continue
                
            for d in os.listdir(s_dir):
                if d.startswith("__") or d.startswith("."):
                    continue
                
                # Deduplicate? Or merge?
                # If same category exists in multiple dirs, we treat them as same category bucket.
                # But we only need metadata once.
                if d in seen_categories:
                    continue
                    
                cat_path = os.path.join(s_dir, d)
                if os.path.isdir(cat_path):
                    # Try to read CATEGORY.md
                    cat_md_path = os.path.join(cat_path, "CATEGORY.md")
                    description = "No description."
                    if os.path.exists(cat_md_path):
                        try:
                            with open(cat_md_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            meta, _ = parse_frontmatter(content)
                            description = meta.get('description', description)
                        except Exception:
                            pass
                    
                    categories.append(CategoryMetadata(
                        name=d,
                        description=description,
                        path=cat_path # This path is just one of them. 
                        # Ideally CategoryMetadata should handle multiple paths if we want to merge contents.
                        # But for now, let's just point to the first one found for description purposes.
                        # list_skills will scan all.
                    ))
                    seen_categories.add(d)
        return categories

    def list_skills(self) -> list[SkillMetadata]:
        """
        Scans for skills across all categories and returns lightweight metadata.
        Level 1 Loading.
        """
        skills = []
    def list_skills(self) -> list[SkillMetadata]:
        """
        Scans for skills across all categories and directories.
        """
        skills = []
        
        # We need to scan all dirs.
        # But get_categories only returned unique category names pointing to the FIRST path.
        # We need to iterate dirs manually or make get_categories return all paths.
        
        # Let's iterate all configured dirs.
        for s_dir in self.skills_dirs:
            if not os.path.exists(s_dir):
                continue
                
            for cat_name in os.listdir(s_dir):
                if cat_name.startswith("__") or cat_name.startswith("."):
                    continue
                    
                cat_dir = os.path.join(s_dir, cat_name)
                if not os.path.isdir(cat_dir):
                    continue
                    
                # Scan skills in this category dir
                for item in os.listdir(cat_dir):
                    skill_path = os.path.join(cat_dir, item)
                    if os.path.isdir(skill_path):
                        md_path = os.path.join(skill_path, "SKILL.md")
                        if os.path.exists(md_path):
                            try:
                                with open(md_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                metadata, _ = parse_frontmatter(content)
                                skills.append(SkillMetadata(
                                    name=metadata.get('name', item),
                                    description=metadata.get('description', 'No description.'),
                                    path=skill_path,
                                    category=cat_name
                                ))
                            except Exception:
                                pass
        return skills

    def load_skill(self, name: str) -> Skill:
        """
        Fully loads a skill by name, including instructions.
        Level 2 Loading.
        """
        # Efficient lookup could employ a cache map from list_skills, 
        # but for now we search again to be robust.
        skills_meta = self.list_skills()
        for meta in skills_meta:
            if meta.name == name:
                md_path = os.path.join(meta.path, "SKILL.md")
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    _, instructions = parse_frontmatter(content)
                    return Skill(metadata=meta, instructions=instructions)
                except Exception as e:
                    print(f"Error loading skill {name}: {e}")
                    return None
        return None

# Backward compatibility functions (optional, but good for transition)
def get_categories(skills_dirs: list[str] = None) -> list[str]:
    return [c.name for c in SkillRegistry(skills_dirs).get_categories()]

def list_skills_in_category(category: str, skills_dirs: list[str] = None) -> list[dict]:
    registry = SkillRegistry(skills_dirs)
    all_skills = registry.list_skills()
    return [
        {
            "name": s.name,
            "description": s.description,
            "path_name": os.path.basename(s.path)
        }
        for s in all_skills if s.category == category
    ]

def search_skills(query: str, skills_dirs: list[str] = None) -> list[dict]:
    registry = SkillRegistry(skills_dirs)
    all_skills = registry.list_skills()
    query = query.lower()
    matches = []
    for s in all_skills:
        if query in s.name.lower() or query in s.description.lower():
            matches.append({
                "name": s.name,
                "description": s.description,
                "category": s.category
            })
    return matches

def load_skill_by_name(skill_name: str, skills_dirs: list[str] = None) -> Skill:
    return SkillRegistry(skills_dirs).load_skill(skill_name)

