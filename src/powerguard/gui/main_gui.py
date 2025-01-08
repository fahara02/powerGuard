import logging
import sys

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit

from powerguard.gui.powerGUard_ui import Ui_MainWindow


def setGui():
    print("gui setup...")

class QTextEditLogger(QObject):
    message_signal = Signal(str)

    def __init__(self):
        super().__init__()

    def write(self, message):
        if message.strip():  # Avoid empty lines
            self.message_signal.emit(message)

    def flush(self):
        pass  # Required for compatibility with sys.stdout and sys.stderr
class LogHandler(logging.Handler, QObject):
    log_signal = Signal(str)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record):
        log_entry = self.format(record)
        self.log_signal.emit(log_entry)


class ServerThread(QThread):
    log_signal = Signal(str)

    def __init__(self, server):
        super().__init__()
        self.server = server
        self.running = True  # Flag to manage thread state

    def run(self):
        try:
            while self.running:  # Keep the thread running as long as `running` is True
                self.server.start_server()  # Replace with non-blocking server code
        except Exception as e:
            self.log_signal.emit(f"Server error: {e}")

    def stop(self):
        self.running = False
        if self.server.running:
            self.server.shutdown_server(None, None)  # Gracefully stop the server
        self.quit()  # Exit the thread loop
        self.wait()  # Ensure the thread finishes
class NodeRedThread(QThread):
    log_signal = Signal(str)

    def __init__(self, server):
        super().__init__()
        self.server = server
        self.running = True

    def run(self):
        try:
            # Check if Node-RED is installed
            if not self.server.is_node_red_installed():
                self.log_signal.emit("Node-RED is not installed. Installing...")
                self.server.install_node_red()

            self.log_signal.emit("Starting Node-RED server...")
            self.server.start_server()
            self.log_signal.emit("Node-RED server started successfully.")
        except Exception as e:
            self.log_signal.emit(f"Node-RED initialization error: {e}")

    def stop(self):
        self.running = False
        self.server.shutdown_server(None, None)
        self.quit()
        self.wait()


class MainGUI(QMainWindow, Ui_MainWindow):
    def __init__(self, app, server):
        super().__init__()
        self.setupUi(self)
        self.app = app
        self.server = server

        self.server_thread = ServerThread(self.server)
        self.server_thread.log_signal.connect(self.append_log)
        self.stackedWidget.setCurrentWidget(self.main_page) 
        # Node-RED thread setup
        self.nodered_thread = NodeRedThread(self.server)
        self.nodered_thread.log_signal.connect(self.append_log)

        self.setup_logging()
        self.redirect_stdout()

        # Button connections
        self.btnServer.clicked.connect(self.start_server)
        self.btnNodeRedInit.clicked.connect(self.init_nodered)
        self.btnBrowser.clicked.connect(self.redirect_to_browser_page)

    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def closeEvent(self, event):
        """Handle the GUI close event."""
        if self.server_thread.isRunning():
            self.append_log("Stopping server thread...")
            self.server_thread.stop()
            self.server_thread.wait()
        if self.nodered_thread.isRunning():
            self.append_log("Stopping Node-RED thread...")
            self.nodered_thread.stop()
            self.nodered_thread.wait()
        self.server.shutdown_server(None, None)
        super().closeEvent(event)


    def setup_logging(self):
        self.logger = logging.getLogger("ServerLogger")
        self.logger.setLevel(logging.DEBUG)

        log_handler = LogHandler()
        log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        log_handler.log_signal.connect(self.append_log)

        self.logger.addHandler(log_handler)

    def  redirect_stdout(self):
        """Redirect stdout and stderr to append_log."""
        self.text_edit_logger = QTextEditLogger()
        self.text_edit_logger.message_signal.connect(self.append_log)
        sys.stdout = self.text_edit_logger
        sys.stderr = self.text_edit_logger

    def redirect_to_browser_page(self):
        """
        Switch to the browser page and load the Node-RED URL.
        """
        try:
            ip_address = self.server.get_ip_address()
            node_red_url = f"http://{ip_address}:1880/"
            self.stackedWidget.setCurrentWidget(self.browser_page)  # Switch to browser_page
            self.webEngineView.setUrl(node_red_url)  # Set the URL in QWebEngineView
            self.append_log(f"Redirecting to Node-RED page: {node_red_url}")
        except Exception as e:
            self.append_log(f"Error redirecting to browser page: {e}")

    def append_log(self, message: str):
        self.sysLog.append(message.strip())

    def start_server(self):
        """Start the server in a separate thread."""
        if self.server:
            try:
                if not self.server_thread.isRunning():
                    self.server_thread.start()
                    self.append_log("Server is starting...")
                else:
                    self.append_log("Server is already running.")
            except Exception as e:
                self.append_log(f"Failed to start server: {e}")
    def init_nodered(self):
         if not self.nodered_thread.isRunning():
            try:
                self.nodered_thread.start()
                self.append_log("Node-RED initialization started...")
            except Exception as e:
                self.append_log(f"Failed to start Node-RED initialization: {e}")



if __name__ == "__main__":
    class MockServer:
        def start_server(self):
            import time
            for i in range(5):
                time.sleep(1)
                print(f"Running task {i + 1}...")

    app = QApplication(sys.argv)
    server = MockServer()
    window = MainGUI(app, server)
    window.show()
    sys.exit(app.exec())











