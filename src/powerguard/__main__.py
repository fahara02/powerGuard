import os
import sys
from pathlib import Path

from powerguard.bootstrap import paths
from powerguard.data import DataManager
from powerguard.gui import setGui
from powerguard.report import ReportGenerator
from powerguard.server import Server, ServerConfig
from powerguard.UPS_Test import TestManager

# Debugging: Print configured paths
print("Paths configured:")
for name, path in paths.items():
    print(f"{name}: {path}")

data_manager = DataManager()
server_config = ServerConfig(
    host="0.0.0.0",
    port=12345,
    node_red_dir="node-red",
    flows_file="flows_modbus.json",
)
server = Server(server_config, data_manager)
report_generator = ReportGenerator(data_manager=data_manager)
test_manager = TestManager()


def main():
    print("Hello from powerguard!")
    print("Setting up database")

    setGui()
    server.start_server()


if __name__ == "__main__":
    main()
