from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QTabWidget
from PyQt5.QtCore import pyqtSignal, Qt
import json
import server_runner

class HomeScreen(QWidget):
    server_selected = pyqtSignal(dict, int)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Load server data from JSON file
        with open('servers.json', 'r') as file:
            self.servers = json.load(file)

        # List widget for displaying servers
        self.server_list_widget = QListWidget(self)
        for index, server in enumerate(self.servers):
            item = QListWidgetItem(server['name'])
            self.server_list_widget.addItem(item)
        self.server_list_widget.itemClicked.connect(self.on_server_selected)
        layout.addWidget(self.server_list_widget)

        self.setLayout(layout)

    def on_server_selected(self, item):
        selected_index = self.server_list_widget.row(item)
        selected_server = self.servers[selected_index]
        self.server_selected.emit(selected_server, selected_index)

class ServerTab(QWidget):
    run_server_signal = pyqtSignal(str)  # Signal to pass path to run_server function

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Add a button to run the server
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_button_clicked)  # Connect button click to function
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def run_button_clicked(self):
        server_path = "servers/" + self.server_name + "/run.bat"  # Construct server path
        self.run_server_signal.emit(server_path)  # Emit signal with path to run_server function

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Server Wrapper')

        # Create home screen and server tab
        self.home_screen = HomeScreen()
        self.server_tab = ServerTab()

        # Add home screen to main window
        self.setCentralWidget(self.home_screen)

        # Connect signals and slots
        self.home_screen.server_selected.connect(self.on_server_selected)
        self.server_tab.run_server_signal.connect(self.run_server)

    def on_server_selected(self, server_data, index):
        self.server_tab.server_name = server_data['truename']  # Store server name
        # Add server tab to main window
        self.setCentralWidget(self.server_tab)

    def run_server(self, server_path):
        server_runner.run_server(server_path)  # Run server with provided path

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
