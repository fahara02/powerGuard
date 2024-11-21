import json
import os
import platform
import socket
import subprocess

import netifaces
import requests

from proto import message_pb2


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
        self.node_red_dir = node_red_dir
        self.flows_file = flows_file
        self.server_socket = None
        self.install_node_red_if_needed()  # Install Node-RED if needed

    def get_ip_address(self):
        """Fetch the local IP address of the machine (non-loopback)."""
        for interface in netifaces.interfaces():
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for addr in addresses[netifaces.AF_INET]:
                    if addr["addr"] != "127.0.0.1":  # Skip localhost
                        return addr["addr"]
        return "127.0.0.1"

    def is_node_red_installed(self):
        """Check if Node-RED is installed by looking for the executable."""
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
                self.install_node_red()
            else:
                print("Node-RED must be installed to run the server.")
                exit(1)

    def install_node_red(self):
        """Install Node-RED locally in the specified directory."""
        if not os.path.exists(self.node_red_dir):
            os.makedirs(self.node_red_dir)
            print(f"Created Node-RED directory: {self.node_red_dir}")

        node_modules_path = os.path.join(self.node_red_dir, "node_modules")
        if not os.path.exists(node_modules_path):
            print("Installing Node-RED locally...")

            is_windows = platform.system().lower() == "windows"
            try:
                # Initialize a Node.js project
                subprocess.run(
                    ["npm", "init", "-y"],
                    cwd=self.node_red_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=is_windows,
                    check=True,
                )
                # Install Node-RED
                subprocess.run(
                    ["npm", "install", "node-red"],
                    cwd=self.node_red_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=is_windows,
                    check=True,
                )
                print("Node-RED installed locally.")

                # Install additional palette (e.g., node-red-dashboard)
                self.install_node_red_palette()
            except subprocess.CalledProcessError as e:
                print(f"Failed to install Node-RED: {e}")
                exit(1)

    def install_node_red_palette(self):
        """Install the Node-RED palette after Node-RED is installed."""
        print("Installing Node-RED palettes")
        packages = [
            "@flowfuse/node-red-dashboard",
            "node-red-contrib-modbus",
            "node-red-contrib-modbus-flex-server",
        ]
        try:
            is_windows = platform.system().lower() == "windows"
            for package in packages:
                print(f"Installing {package}...")
                subprocess.run(
                    ["npm", "install", package],
                    cwd=self.node_red_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=is_windows,
                    check=True,
                )
                print(f"Installed {package} successfully.")
            print("Node-RED palette {package} installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Node-RED palette {package} : {e}")
            exit(1)

    def import_flow(self):
        """Import flow from flows_modbus.json into Node-RED via its REST API."""
        flow_file_path = self.flows_file

        # Read the flow from the file
        with open(flow_file_path, "r") as file:
            flow_data = json.load(file)

        # URL to the Node-RED flows endpoint
        node_red_url = f"http://{self.get_ip_address()}:1880/flows"

        try:
            # POST the flow data to Node-RED
            response = requests.post(node_red_url, json=flow_data)
            response.raise_for_status()  # Check for errors

            if response.status_code == 204:
                print("Flow imported and deployed successfully.")
            else:
                print(
                    f"Failed to import flow: {response.status_code} - {response.text}"
                )
        except requests.RequestException as e:
            print(f"Error importing flow: {e}")

    def start_node_red(self):
        """Start the Node-RED server."""
        node_red_exec = os.path.join(
            self.node_red_dir,
            "node_modules",
            ".bin",
            "node-red.cmd" if platform.system().lower() == "windows" else "node-red",
        )

        if os.path.exists(node_red_exec):
            print(f"Starting Node-RED server in directory: {self.node_red_dir}")
            try:
                subprocess.Popen(
                    [node_red_exec, "--userDir", self.node_red_dir],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print(
                    f"Node-RED server started. Access it at: http://{self.get_ip_address()}:1880/"
                )
            except Exception as e:
                print(f"Failed to start Node-RED: {e}")
        else:
            print("Node-RED executable not found. Ensure it is installed correctly.")
            exit(1)

    def start_server(self):
        """Start the TCP server to handle protobuf messages."""
        try:
            self.start_node_red()
            self.import_flow()

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection established with {address}")

                try:
                    data = client_socket.recv(1024)  # Adjust buffer size if needed
                    if not data:
                        break

                    # Decode the received protobuf message
                    sensor_data = message_pb2.SensorData()
                    sensor_data.ParseFromString(data)

                    print("Received data:")
                    print(f"ID: {sensor_data.id}")
                    print(f"Name: {sensor_data.name}")
                    print(f"Value: {sensor_data.value}")

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


if __name__ == "__main__":
    server = Server()
    server.start_server()
