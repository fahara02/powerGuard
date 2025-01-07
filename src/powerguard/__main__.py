import os
import signal
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from powerguard.bootstrap import paths
from powerguard.data import DataManager
from powerguard.gui import MainGUI, setGui
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
    node_red_folder="node-red",
    flows_folder="flows",
)
server = Server(server_config, data_manager)
report_generator = ReportGenerator(data_manager=data_manager)
test_manager = TestManager()

def handle_sigint(signal, frame):
    print("Gracefully shutting down...")
    if server.running:
        server.running = False
        server.shutdown_server(signal, frame)
    QApplication.quit()


def main():
    signal.signal(signal.SIGINT, handle_sigint)
  
    app = QApplication(sys.argv)
    window = MainGUI(app, server)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


 # print("Hello from powerguard!")
   #print("Setting up database")
   #setGui()
    #server.start_server()