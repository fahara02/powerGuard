from powerguard.path_utils import set_project_paths

# Set up project paths
paths = set_project_paths()

# Expose paths for use in other scripts
__all__ = ["paths"]
