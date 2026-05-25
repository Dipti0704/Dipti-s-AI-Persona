import json
from pathlib import Path
from typing import List, Dict, Any

KNOWLEDGE_DIR = Path(__file__).parent.resolve()

def get_resume_chunks() -> List[Dict[str, Any]]:
    resume_path = KNOWLEDGE_DIR / "resume_text.txt"
    if not resume_path.exists():
        return []
        
    with open(resume_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    chunks = []
    
    # We split resume semantically by sections
    sections = content.split("\n\n")
    
    # Group sections logically
    # Chunk 1: Contact Info
    contact_info = sections[0]
    chunks.append({
        "id": "resume_contact",
        "content": contact_info,
        "metadata": {
            "source": "resume",
            "topic": "contact",
            "title": "Dipti Hatwar Contact Info"
        }
    })
    
    for section in sections[1:]:
        lines = section.strip().split("\n")
        if not lines:
            continue
        title = lines[0].strip()
        
        # Experience Chunk
        if "Experience" in title:
            chunks.append({
                "id": "resume_experience",
                "content": section,
                "metadata": {
                    "source": "resume",
                    "topic": "experience",
                    "title": "Professional Experience: WNS-VURAM AI Research Intern"
                }
            })
        # Projects Chunk
        elif "Projects" in title:
            chunks.append({
                "id": "resume_projects",
                "content": section,
                "metadata": {
                    "source": "resume",
                    "topic": "projects",
                    "title": "Resume Project Summary"
                }
            })
        # Education Chunk
        elif "Education" in title:
            chunks.append({
                "id": "resume_education",
                "content": section,
                "metadata": {
                    "source": "resume",
                    "topic": "education",
                    "title": "Education: Scaler School of Tech & BITS Pilani"
                }
            })
        # Technical Skills Chunk
        elif "Technical Skills" in title or "Skills" in title:
            chunks.append({
                "id": "resume_skills",
                "content": section,
                "metadata": {
                    "source": "resume",
                    "topic": "skills",
                    "title": "Technical Skills: Languages, AI/ML, Web Frameworks"
                }
            })
        # Position of Responsibility Chunk
        elif "POSITION" in title or "Responsibility" in title:
            chunks.append({
                "id": "resume_responsibility",
                "content": section,
                "metadata": {
                    "source": "resume",
                    "topic": "responsibility",
                    "title": "Position of Responsibility: Placement Cell Secretary"
                }
            })
            
    return chunks

def get_project_chunks() -> List[Dict[str, Any]]:
    db_path = KNOWLEDGE_DIR / "projects_db.json"
    if not db_path.exists():
        return []
        
    with open(db_path, "r", encoding="utf-8") as f:
        projects = json.load(f)
        
    chunks = []
    for proj in projects:
        # Construct highly detailed textual representation of the project
        proj_id = proj["id"]
        name = proj["name"]
        subtitle = proj["subtitle"]
        purpose = proj["purpose"]
        tech = ", ".join(proj["tech_stack"])
        arch = proj["architecture"]
        pros = "\n  - ".join(proj["tradeoffs"]["pros"])
        cons = "\n  - ".join(proj["tradeoffs"]["cons"])
        features = "\n  - ".join(proj["features"])
        
        content = (
            f"Project: {name} ({subtitle})\n"
            f"Purpose: {purpose}\n"
            f"Tech Stack: {tech}\n"
            f"Architecture: {arch}\n"
            f"Key Trade-offs (Pros):\n  - {pros}\n"
            f"Key Trade-offs (Cons):\n  - {cons}\n"
            f"Key Features:\n  - {features}"
        )
        
        chunks.append({
            "id": f"project_{proj_id}",
            "content": content,
            "metadata": {
                "source": "github_projects",
                "topic": proj_id,
                "title": f"Project Details: {name}",
                "tech_stack": proj["tech_stack"]
            }
        })
        
    return chunks

def get_all_chunks() -> List[Dict[str, Any]]:
    return get_resume_chunks() + get_project_chunks()
