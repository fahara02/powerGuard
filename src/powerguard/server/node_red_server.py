import json
import os
import platform
import subprocess
import time
from pathlib import Path

import netifaces
import requests


class NodeRedServer:
    def __init__(self, node_red_dir: Path, flows_file: Path):
        """
        Initialize the Node-RED server instance.

        Args:
            node_red_dir (Path): Path to the Node-RED directory.
            flows_file (Path): Path to the flows configuration file.
        """
        self.node_red_dir = node_red_dir
        self.flows_file = flows_file

        # Ensure the directory and file paths are valid
        self._validate_paths()

    def _validate_paths(self):
        """Validate that the provided paths exist or are valid."""
        if not self.node_red_dir.exists():
            raise FileNotFoundError(
                f"Node-RED directory not found: {self.node_red_dir}"
            )

        if not self.flows_file.exists():
            raise FileNotFoundError(f"Flows file not found: {self.flows_file}")

    def get_ip_address(self):
        """Fetch the local IP address of the machine (non-loopback)."""
        for interface in netifaces.interfaces():
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for addr in addresses[netifaces.AF_INET]:
                    if addr["addr"] != "127.0.0.1":  # Skip localhost
                        return addr["addr"]
        return "127.0.0.1"

    def install(self):
        """Install Node-RED locally."""
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
                print("Node-RED installed successfully.")

            except subprocess.CalledProcessError as e:
                print(f"Failed to install Node-RED: {e}")
                exit(1)

    def install_palettes(self):
        """Install additional Node-RED palettes."""
        print("Installing Node-RED palettes")
        palettes = [
            "@flowfuse/node-red-dashboard",
            "node-red-contrib-modbus",
            "node-red-contrib-modbus-flex-server",
        ]
        try:
            is_windows = platform.system().lower() == "windows"
            for palette in palettes:
                print(f"Installing {palette}...")
                subprocess.run(
                    ["npm", "install", palette],
                    cwd=self.node_red_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=is_windows,
                    check=True,
                )
                print(f"Installed palette: {palette}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install palettes {palette}: {e}")
            exit(1)

    def start(self):
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
                    f"Node-RED started. Access it at http://{self.get_ip_address()}:1880/"
                )
            except Exception as e:
                print(f"Failed to start Node-RED: {e}")
                exit(1)

    def wait_until_ready(self, timeout=30):
        """Wait for Node-RED to be ready."""
        node_red_url = f"http://{self.get_ip_address()}:1880"
        for _ in range(timeout):
            try:
                response = requests.get(node_red_url)
                if response.status_code == 200:
                    print("Node-RED is ready.")
                    return True
            except requests.ConnectionError:
                pass
            time.sleep(1)
        print("Node-RED did not respond in time.")
        return False

    def import_flows(self):
        """Import flows into Node-RED."""
        try:
            with open(self.flows_file, "r") as file:
                flow_data = json.load(file)

            node_red_url = f"http://{self.get_ip_address()}:1880/flows"
            response = requests.post(node_red_url, json=flow_data)
            response.raise_for_status()

            if response.status_code == 204:
                print("Flows imported and deployed successfully.")
            else:
                print(f"Failed to import flows: {response.status_code}")
        except Exception as e:
            print(f"Error importing flows: {e}")
            print(f"Error importing flows: {e}")
