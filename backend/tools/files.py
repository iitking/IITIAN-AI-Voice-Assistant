"""
IITIAN AI - File and Project Finder Tool
Finds projects, files, and directories, and opens them in editor or Finder.
"""

import os
import platform
import subprocess
from pathlib import Path
from backend.config import BASE_DIR

def search_project_or_file(name: str) -> dict:
    """
    Searches for a project folder or file matching the given name and opens it.
    """
    clean_name = name.strip().lower()
    
    # Common search roots: current workspace, user desktop, documents
    user_home = Path.home()
    search_dirs = [
        BASE_DIR.parent,
        user_home / "Desktop",
        user_home / "Documents",
        user_home / "Projects",
        BASE_DIR
    ]

    found_path = None
    for root in search_dirs:
        if not root.exists():
            continue
        try:
            for item in root.iterdir():
                if clean_name in item.name.lower():
                    found_path = item
                    break
        except Exception:
            continue
        if found_path:
            break

    if found_path:
        # Open in VS Code or Finder
        opened_with = "Finder"
        try:
            if platform.system() == "Darwin":
                # Try opening in VS Code if it's a project
                res = subprocess.run(["open", "-a", "Visual Studio Code", str(found_path)], capture_output=True)
                if res.returncode == 0:
                    opened_with = "VS Code"
                else:
                    subprocess.run(["open", str(found_path)])
        except Exception:
            pass

        return {
            "success": True,
            "name": found_path.name,
            "path": str(found_path),
            "opened_with": opened_with,
            "message": f"Found '{found_path.name}' at {found_path} and opened in {opened_with}."
        }
    else:
        return {
            "success": False,
            "query": name,
            "message": f"Could not find project or file matching '{name}'. Looked in Desktop and Documents."
        }

def list_recent_files(directory: str = "") -> dict:
    """Lists files in the target directory."""
    target = Path(directory) if directory else BASE_DIR
    if not target.exists():
        return {"success": False, "message": f"Directory '{directory}' does not exist."}
    
    items = []
    try:
        for p in list(target.iterdir())[:15]:
            items.append({
                "name": p.name,
                "is_dir": p.is_dir(),
                "size_bytes": p.stat().st_size if p.is_file() else 0
            })
        return {"success": True, "path": str(target), "files": items}
    except Exception as e:
        return {"success": False, "error": str(e)}
