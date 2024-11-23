import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
proto_dir = os.path.join(parent_dir, "proto")
data_dir = os.path.join(parent_dir, "data")

# Add parent, proto, and data directories to sys.path
for directory in [parent_dir, proto_dir, data_dir]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

# Debugging - print sys.path for verification
print("Updated sys.path:", sys.path)

from powerguard.gui import setGui
from powerguard.server import Server
from data import DataManager


server = Server()


def main():
    print("Hello from powerguard!")
    print("Setting up database")
    dataManager=DataManager()

    setGui()
    server.start_server()


if __name__ == "__main__":
    main()
