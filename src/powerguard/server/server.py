# import os
import os
import platform
import socket
import threading
from pathlib import Path
from typing import Optional, Type

from pydantic import BaseModel, Field, field_validator

from powerguard.bootstrap import paths
from powerguard.data.data_manager import DataManager
from powerguard.server.node_red_server import NodeRedServer
from proto.report_pb2 import TestReport


# Pydantic model for Server configuration
class ServerConfig(BaseModel):
    
    host: str = Field(default="0.0.0.0", description="Host address")
    port: int = Field(default=12345, description="Port number")

    node_red_folder: str = Field(
        default="node-red", description="Node-RED directory path"
    )
    flows_folder: str = Field(default="flows", description="Flows directory path")

    @field_validator("host")
    def validate_host(cls, v):
        """Ensure the host is a valid IP address or a hostname."""
        if not v or not isinstance(v, str):
            raise ValueError("Invalid host value")
        return v

    @field_validator("port")
    def validate_port(cls, v):
        """Ensure the port number is between 1 and 65535."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


class Server(BaseModel):
    config: ServerConfig  # This is the Pydantic model containing configuration
    data_manager: DataManager  # Expecting a DataManager instance
    node_red_path: Optional[Path] = None
    flows_dir_path: Optional[Path] = None
    node_red: NodeRedServer = None
    server_socket: socket.socket = None
    running: bool = False

    class Config:
        # This tells Pydantic to ignore extra fields during initialization
        extra = "ignore"
        arbitrary_types_allowed = True

    def __init__(self, config: ServerConfig, data_manager: DataManager):
        super().__init__(config=config, data_manager=data_manager)
      
        # Ensure Node-RED directory is set up
        node_red_folder = paths["node_red_dir"]
        node_red_folder.mkdir(parents=True, exist_ok=True)
        # Set the Node-RED path if not provided
        if not self.node_red_path:
            self.node_red_path = node_red_folder

        flows_dir = paths["flows_dir"]

        # Set the flows file path if not provided
        if not self.flows_dir_path:
            self.flows_dir_path = flows_dir

        self.node_red = NodeRedServer(self.node_red_path, self.flows_dir_path)
        #self.install_node_red_if_needed()

    def is_node_red_installed(self):
        """Check if Node-RED is installed."""
        node_red_exec = os.path.join(
            self.config.node_red_folder,
            "node_modules",
            ".bin",
            "node-red.cmd" if platform.system().lower() == "windows" else "node-red",
        )
        return os.path.exists(node_red_exec)
    
    def install_node_red(self):
        """Just install node red."""
        try:
         print("Installing node red...")
         self.node_red.install()
        
         print("Installing palletes...")
         self.node_red.install_palettes()
         
        except Exception as e:
            print(f"Error installing nodered: {e}")


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
    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024)
            if not data:
                return

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
    def start_server(self):
        """Start the server and manage communication."""
        self.running = True
        try:
            self.node_red.start()
            if not self.node_red.wait_until_ready():
                print("Node-RED failed to start.")
                return
            self.node_red.start_watchdog()

            self.node_red.import_flows()
            print("Updating settings...")
            self.node_red.configure_context_persistence()
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.config.host, self.config.port))
            self.server_socket.listen(5)
            print(f"Server listening on {self.config.host}:{self.config.port}")

            while self.running:
                self.server_socket.settimeout(1.0)  # Allow periodic checks for shutdown
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"Connection established with {address}")
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_thread.start()
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"Server encountered an error: {e}")
        finally:
            self.shutdown_server(None, None)

    def get_ip_address(self):
        return self.node_red.get_ip_address()

    def shutdown_server(self, signum, frame):
        """Shut down the server gracefully."""
        print("Shutting down server...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("Server socket closed.")
        if self.node_red:
            self.node_red.stop_watchdog()
            self.node_red.stop()  # Ensure Node-RED stops
        if self.data_manager:
            self.data_manager.close()
        print("Server shutdown complete.")


        

if __name__ == "__main__":
    # Create a DataManager instance first
    data_manager = DataManager()

    # Create a ServerConfig instance with the desired configuration
    server_config = ServerConfig(
        host="0.0.0.0",
        port=12345,
        node_red_folder="node-red",
        flows_folder="flows",
    )

    # Now create and start the server, passing in the ServerConfig and DataManager instances
    server = Server(config=server_config, data_manager=data_manager)
    server.start_server()
