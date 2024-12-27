
import os
import sys
from pathlib import Path


def set_project_paths():
    """Set up the necessary project paths globally, resolving the project root directory."""
    # Get the absolute path of the script
    current_dir = Path(__file__).resolve().parent

    # Traverse up to the project root directory by looking for .git or another indicator
    while not (current_dir / ".git").exists():
        current_dir = current_dir.parent
        # Stop if we've reached the root directory (no .git found)
        if current_dir == current_dir.parent:
            raise FileNotFoundError(
                "Could not find the project root directory with a .git folder"
            )

    project_dir = current_dir  # This is the root of the project

    # Define other paths relative to the project root
    parent_dir = project_dir.parent
    proto_dir = project_dir / "src" / "proto"
    node_red_dir = project_dir / "node-red"
    flows_dir = project_dir / "flows"
    template_dir = project_dir / "template"
    output_dir = project_dir / "output"
    db_dir = project_dir / "db"
    dist_dir = project_dir / "dist"
    src_dir = project_dir / "src"

    # Add project directories to sys.path for module imports
    for directory in [
        parent_dir,
        project_dir,
        node_red_dir,
        proto_dir,
        template_dir,
        output_dir,
        db_dir,
        flows_dir,
        dist_dir,
        src_dir,
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
        "node_red_dir": node_red_dir,
        "flows_dir": flows_dir,
        "dist_dir": dist_dir,
        "src_dir": src_dir,
    }
