import os
import sys


def set_project_paths():
    """Set up the necessary project paths globally."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
    project_dir = os.path.abspath(os.path.join(parent_dir, ".."))
    template_dir = os.path.join(project_dir, "template")
    proto_dir = os.path.join(parent_dir, "proto")

    # Add parent, proto, and template directories to sys.path
    for directory in [parent_dir, proto_dir, template_dir]:
        if directory not in sys.path:
            sys.path.insert(0, directory)
     

    # Return the paths for verification if needed
    return {
        "current_dir": current_dir,
        "parent_dir": parent_dir,
        "project_dir": project_dir,
        "template_dir": template_dir,
        "proto_dir": proto_dir,
    }
