import sys
import os
from pathlib import Path


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
proto_dir = os.path.join(parent_dir, "proto")
data_dir = os.path.join(parent_dir, "data")

# Add parent, proto, and data directories to sys.path
for directory in [parent_dir, proto_dir, data_dir]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

# # Debugging - print sys.path for verification
# print("Updated sys.path:", sys.path)

from powerguard.gui import setGui
from powerguard.server import Server,ServerConfig
from data import DataManager
from powerguard.report import ReportGenerator


data_manager = DataManager()

    # Create a ServerConfig instance with the desired configuration
server_config = ServerConfig(host="0.0.0.0", port=12345, node_red_dir="node-red", flows_file="flows/flows_modbus.json")

    # Now create and start the server, passing in the ServerConfig and DataManager instances
server = Server(server_config, data_manager)
# report_generator = ReportGenerator(
#         data_manager=data_manager,
#         template_path=Path("test_report_template.docx")
#     )

def main():
    print("Hello from powerguard!")
    print("Setting up database")
  

    setGui()
    server.start_server()


if __name__ == "__main__":
    main()
