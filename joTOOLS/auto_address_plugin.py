from qgis.core import (
    QgsProject,
    QgsSpatialIndex,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsWkbTypes
)
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QMessageBox,
    QCheckBox
)
from .processing_logic import process_layers
class LayerSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Layers and HUT/DA")

        layout = QVBoxLayout()

        # Filter only vector layers
        layers = QgsProject.instance().mapLayers().values()
        vector_layers = [lyr for lyr in layers if lyr.type() == lyr.VectorLayer]
        layer_names = [lyr.name() for lyr in vector_layers]

        if not layer_names:
            QMessageBox.warning(self, "No Vector Layers", "No vector layers found in the project.")
            return

        
        self.include_da_checkbox = QCheckBox("Include DA Processing")
        self.include_da_checkbox.setChecked(True)  # default to include
        layout.addWidget(self.include_da_checkbox)

        # Layer dropdowns
        self.parcel_combo = QComboBox()
        self.address_combo = QComboBox()
        self.da_combo = QComboBox()

        self.parcel_combo.addItems(layer_names)
        self.address_combo.addItems(layer_names)
        self.da_combo.addItems(layer_names)

        # HUT and DA dropdowns
        self.hut_combo = QComboBox()
        self.da_project_combo = QComboBox()
        self.da_combo.currentIndexChanged.connect(self.update_da_hut_options)

        # Layout rows
        for label_text, combo in [
            ("Parcel Layer:", self.parcel_combo),
            ("Address Layer:", self.address_combo),
            ("DA Boundary Layer:", self.da_combo),
            ("Select HUT:", self.hut_combo),
            ("Select DA:", self.da_project_combo),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addWidget(combo)
            layout.addLayout(row)

        # Buttons: Preview, Run, Cancel
        button_layout = QHBoxLayout()
        self.preview_btn = QPushButton("Preview")
        self.ok_btn = QPushButton("Run")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.preview_btn.clicked.connect(self.preview_parcels)

        # Initialize HUT/DA dropdowns
        self.update_da_hut_options()

    def update_da_hut_options(self):
        self.hut_combo.clear()
        self.da_project_combo.clear()
        da_layer_name = self.da_combo.currentText()
        if not da_layer_name:
            return

        da_layers = QgsProject.instance().mapLayersByName(da_layer_name)
        if not da_layers or da_layers[0].type() != da_layers[0].VectorLayer:
            return

        da_layer = da_layers[0]

        hut_set = set()
        da_project_set = set()

        for feat in da_layer.getFeatures():
            if 'HUT' in feat.fields().names():
                hut_set.add(str(feat['HUT']))
            if 'Project' in feat.fields().names():
                da_project_set.add(str(feat['Project']))

        # Add Hut 1 to Hut 11 manually
        for i in range(1, 12):
            hut_set.add(f"Hut {i}")

        self.hut_combo.addItems(sorted(hut_set))
        self.da_project_combo.addItems(sorted(da_project_set))

    def get_selected_options(self):
        return (
            self.parcel_combo.currentText(),
            self.address_combo.currentText(),
            self.da_combo.currentText(),
            self.hut_combo.currentText(),
            self.da_project_combo.currentText(),
            self.include_da_checkbox.isChecked()
        )


    def preview_parcels(self):
        parcel_name = self.parcel_combo.currentText()
        da_name = self.da_combo.currentText()
        da_project = self.da_project_combo.currentText()

        if not parcel_name or not da_name or not da_project:
            QMessageBox.warning(self, "Missing Selection", "Please select all required layers and DA project.")
            return

        parcel_layers = QgsProject.instance().mapLayersByName(parcel_name)
        da_layers = QgsProject.instance().mapLayersByName(da_name)

        if not parcel_layers or not da_layers:
            QMessageBox.critical(self, "Layer Error", "Selected layers could not be found.")
            return

        parcel_layer = parcel_layers[0]
        da_layer = da_layers[0]

        if parcel_layer.type() != parcel_layer.VectorLayer or da_layer.type() != da_layer.VectorLayer:
            QMessageBox.critical(self, "Layer Type Error", "Selected layers must be vector layers.")
            return
        try:
            da_index = QgsSpatialIndex(da_layer.getFeatures())
            count = 0

            for parcel_feat in parcel_layer.getFeatures():
                centroid = parcel_feat.geometry().centroid()
                if centroid.isEmpty():
                    continue
                da_ids = da_index.intersects(centroid.boundingBox())
                for da_id in da_ids:
                    da_feat = da_layer.getFeature(da_id)
                    if da_feat.geometry().contains(centroid) and da_feat['Project'] == da_project:
                        count += 1
                        break

            QMessageBox.information(self, "Parcel Preview", f"{count} parcel(s) would be processed.")
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"An error occurred during preview:\n{str(e)}")


class AutoAddressPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Auto Address Creator", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Auto Address", self.action)

    def unload(self):
        self.iface.removePluginMenu("&Auto Address", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        dialog = LayerSelectionDialog()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        parcel_name, address_name, da_name, hut_name, da_project, include_da = dialog.get_selected_options()
        added_count = process_layers(parcel_name, address_name, da_name, hut_name, da_project, include_da)


        try:
            added_count = process_layers(parcel_name, address_name, da_name, hut_name, da_project)
            QMessageBox.information(None, "Done", f"{added_count} new address point(s) added with full attributes.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Processing failed:\n{str(e)}")


