import os
import sys
from pathlib import Path


def set_project_paths():
    """Set up the necessary project paths globally."""
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    project_dir = parent_dir.parent
    proto_dir = parent_dir / "proto"
    template_dir = project_dir / "template"
    output_dir = project_dir / "output"
    db_dir = project_dir / "db"

    # Add parent, proto, and template directories to sys.path
    for directory in [
        parent_dir,
        project_dir,
        proto_dir,
        template_dir,
        output_dir,
        db_dir,
    ]:
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))

    # Return the paths for verification if needed
    return {
        "current_dir": current_dir,
        "parent_dir": parent_dir,
        "project_dir": project_dir,
        "template_dir": template_dir,
        "db_dir": db_dir,
        "output_dir": output_dir,
        "proto_dir": proto_dir,
    }
