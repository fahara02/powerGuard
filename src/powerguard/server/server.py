import os
import platform
import socket
import sys


from powerguard.server.node_red_server import NodeRedServer
from proto.report_pb2 import TestReport, ReportSettings



class Server:
    def __init__(
        self,
        host="0.0.0.0",
        port=12345,
        node_red_dir="node-red",
        flows_file="flows/flows_modbus.json",
    ):
        self.host = host
        self.port = port
        self.server_socket = None
        self.node_red_dir = node_red_dir
        self.flows_file = flows_file
        self.node_red = NodeRedServer(node_red_dir, flows_file)
        self.install_node_red_if_needed()  # Install Node-RED if needed
        self.data_manager = DataManager()
    def is_node_red_installed(self):
        """Check if Node-RED is installed."""
        node_red_exec = os.path.join(
            self.node_red_dir,
            "node_modules",
            ".bin",
            "node-red.cmd" if platform.system().lower() == "windows" else "node-red",
        )
        return os.path.exists(node_red_exec)

    def install_node_red_if_needed(self):
        """Check if Node-RED is installed, and prompt the user to install it if not."""
        if not self.is_node_red_installed():
            print("Node-RED is not installed.")
            user_choice = input("Would you like to install Node-RED now? [Y/n]: ")
            if user_choice.lower() in ["y", "yes", ""]:
                self.node_red.install()
            else:
                print("Node-RED must be installed to run the server.")
                exit(1)
    def process_and_store_report(self, report_data: TestReport):
        """Process and store a TestReport message in the database."""
        try:
            print("Storing TestReport in the database...")
            self.data_manager.insert_test_report(report_data)
            print("TestReport successfully stored.")
        except Exception as e:
            print(f"Error storing TestReport: {e}")
    def start_server(self):
        """Start the server and manage communication."""
        try:
            self.node_red.install()
            self.node_red.install_palettes()
            self.node_red.start()

            if not self.node_red.wait_until_ready():
                exit(1)

            self.node_red.import_flows()

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection established with {address}")

                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    report_data = TestReport()
                    report_data.ParseFromString(data)

                    print("Received data:")
                    print(f"ID: {report_data.settings.report_id}")
                    print(f"Name: {report_data.testDescription}")
                    print(f"Description: {report_data.value}")

                    # Store in database
                    self.process_and_store_report(report_data)
                    
                except Exception as e:
                    print(f"Error processing data: {e}")
                finally:
                    client_socket.close()
        except Exception as e:
            print(f"Server encountered an error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
                print("Server socket closed.")
                self.data_manager.close()


if __name__ == "__main__":
    server = Server()
    server.start_server()
