from PyQt6.QtCore import Qt
from qgis.PyQt.QtWidgets import QAction
from .joTOOLS import joTOOLSWindow

class joTOOLSPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dock_widget = None

    def initGui(self):
        self.action = QAction("Open joTOOLS", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&joTOOLS", self.action)

    def unload(self):
        self.iface.removePluginMenu("&joTOOLS", self.action)
        if self.dock_widget:
            self.iface.removeDockWidget(self.dock_widget)

    def run(self):
        if not self.dock_widget:
            self.dock_widget = joTOOLSWindow(self.iface)
        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_widget)
        self.dock_widget.show()

