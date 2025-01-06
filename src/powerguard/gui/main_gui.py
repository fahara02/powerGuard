from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QBrush, QColor, QGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QMainWindow

from powerguard.gui.powerGUard_ui import Ui_MainWindow


class MainGUI(QMainWindow, Ui_MainWindow):

    def __init__(self, app, server):
        """
        Initialize the GUI and connect UI elements to actions.
        
        Args:
            app (QApplication): The Qt application instance.
            server: The server object to be controlled by the GUI.
        """
        super().__init__()
        self.setupUi(self)  # Sets up the UI defined in Ui_MainWindow
        self.app = app
        self.server = server  # Store the server instance

        # Connect the btnServer button to the start_server method
        self.btnServer.clicked.connect(self.start_server)

        self.setWindowTitle("PowerGuard")

    def start_server(self):
        """
        Start the server when the button is clicked.
        """
        if self.server:
            try:
                self.server.start_server()
                print("Server started successfully!")
            except Exception as e:
                print(f"Failed to start server: {e}")


def setGui():
    print("set up gui")


if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    # Mock server object for demonstration
    class MockServer:
        def start_server(self):
            print("Mock server started.")

    app = QApplication(sys.argv)
    server = MockServer()
    window = MainGUI(app, server)
    window.show()
    sys.exit(app.exec())
    window.show()
    sys.exit(app.exec())
