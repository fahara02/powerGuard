import json
import os
import platform
import subprocess
import threading
import time
from pathlib import Path

import netifaces
import requests


class NodeRedServer:
    def __init__(self, node_red_dir: Path, flows_dir: Path):
        """
        Initialize the Node-RED server instance.

        Args:
            node_red_dir (Path): Path to the Node-RED directory.
            flows_file (Path): Path to the flows configuration file.
        """
        self.node_red_dir = node_red_dir
        self.flows_dir= flows_dir
        self.node_red_process = None
        self._watchdog_thread = None
        self._stop_watchdog = threading.Event()

        # Ensure the directory and file paths are valid
        self._validate_paths()

    def _validate_paths(self):
        """Validate that the provided paths exist or are valid."""
        if not self.node_red_dir.exists():
            raise FileNotFoundError(
                f"Node-RED directory not found: {self.node_red_dir}"
            )

        if not self.flows_dir.exists():
            raise FileNotFoundError(f"Flows file not found: {self.flows_dir}")
    def _is_server_running(self):
        """Check if the Node-RED server is running and responsive."""
        node_red_url = f"http://{self.get_ip_address()}:1880"
        try:
            response = requests.get(node_red_url, timeout=5)
            return response.status_code == 200
        except requests.ConnectionError:
            return False
    def start_watchdog(self):
        """Start a watchdog to monitor and restart the Node-RED server."""
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            print("Watchdog is already running.")
            return

        def watchdog():
            while not self._stop_watchdog.is_set():
                if not self._is_server_running():
                    print("Node-RED server is not responsive. Restarting...")
                    self.stop()
                    self.start()
                time.sleep(10)  # Check every 10 seconds

        self._watchdog_thread = threading.Thread(target=watchdog, daemon=True)
        self._stop_watchdog.clear()
        self._watchdog_thread.start()
        print("Watchdog started.") 
    def stop_watchdog(self):
        """Stop the watchdog process."""
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            self._stop_watchdog.set()
            self._watchdog_thread.join()
            print("Watchdog stopped.")       

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
            "@flowfuse/node-red-dashboard-2-ui-led",
            "@colinl/node-red-dashboard-2-ui-gauge-classic",
            "node-red-contrib-protobuf",
            "node-red-contrib-fs",
            "node-red-node-sqlite",
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
        """Start the Node-RED server in a subprocess."""
        def run_node_red():
            node_red_exec = os.path.join(
                self.node_red_dir,
                "node_modules",
                ".bin",
                "node-red.cmd" if platform.system().lower() == "windows" else "node-red",
            )
            if os.path.exists(node_red_exec):
                print(f"Starting Node-RED server in directory: {self.node_red_dir}")
                try:
                    # Start Node-RED in a subprocess and capture the process
                    self.node_red_process = subprocess.Popen(
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

        if self.node_red_process and self.node_red_process.poll() is None:
            print("Node-RED is already running.")
            return
        node_red_thread = threading.Thread(target=run_node_red, daemon=True)
        node_red_thread.start()

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
        """Import all flows from the flows directory into Node-RED."""
        try:
            flow_data_combined = []
            # Load all JSON files in the flows directory
            for flow_file in self.flows_dir.glob("*.json"):
                print(f"Loading flow file: {flow_file}")
                with open(flow_file, "r") as file:
                    flow_data = json.load(file)
                    flow_data_combined.extend(flow_data)

            if not flow_data_combined:
                print("No valid flow files found in the directory.")
                return

            # Send combined flow data to Node-RED
            node_red_url = f"http://{self.get_ip_address()}:1880/flows"
            response = requests.post(node_red_url, json=flow_data_combined)
            response.raise_for_status()

            if response.status_code == 204:
                print("All flows imported and deployed successfully.")
            else:
                print(f"Failed to import flows: {response.status_code}")
        except Exception as e:
            print(f"Error importing flows: {e}")
            print(f"Error importing flows: {e}")

    def stop(self):
        """Stop the Node-RED server process."""
        if self.node_red_process:
            print("Stopping Node-RED...")
            try:
                self.node_red_process.terminate()  # Attempt to terminate
                self.node_red_process.wait(timeout=5)  # Wait for clean exit
            except subprocess.TimeoutExpired:
                print("Node-RED did not terminate. Forcing shutdown...")
                self.node_red_process.kill()  # Force kill if not responsive
            finally:
                self.node_red_process = None
            print("Node-RED stopped.")
        else:
            print("Node-RED process not running.")
