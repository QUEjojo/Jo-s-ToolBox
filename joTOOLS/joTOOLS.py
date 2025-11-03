from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QDialog,
    QMessageBox, QHBoxLayout, QFormLayout, QLineEdit, QListWidget, QSpinBox, QCheckBox,
    QAbstractItemView, QListWidgetItem,QInputDialog, QProgressBar, QTabWidget, QGridLayout, QTabWidget, QSlider
)
import math
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsProject, QgsSpatialIndex, QgsWkbTypes, QgsGeometry, QgsPointXY, QgsMapLayer
)
from qgis.core import (
    QgsMapLayerType, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsWkbTypes, QgsSpatialIndex
)
from PyQt6.QtCore import QVariant, Qt
from PyQt6.QtGui import QIntValidator
from .auto_address_plugin import LayerSelectionDialog
from .processing_logic import process_layers
import math
class joTOOLSWindow(QDockWidget):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("joTOOLS")

        # Main widget and layout
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        main_layout = QVBoxLayout()

        #Welcome label
        welcome_label = QLabel("Welcome to the Toolbox!")
        main_layout.addWidget(welcome_label)

        #Tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        #Address Tools Tab
        address_tab = QWidget()
        address_layout = QVBoxLayout()

        #Parcel Tools Tab
        parcel_tab = QWidget()
        parcel_layout = QVBoxLayout()

        #Other Tools Tab
        other_tab = QWidget()
        other_layout = QVBoxLayout()

        #Buttons for each address-related tool
        btn_auto_address = QPushButton("Auto Address Creator")
        btn_auto_address.clicked.connect(self.launch_auto_address_dialog)
        address_layout.addWidget(btn_auto_address)

        btn_centralize = QPushButton("Centralize Address Points")
        btn_centralize.clicked.connect(self.launch_centralize_address_points_dialog)
        address_layout.addWidget(btn_centralize)
        
        btn_delete_points = QPushButton("Delete Points Without External IDs")
        btn_delete_points.clicked.connect(self.launch_delete_points_without_external_ids_dialog)
        address_layout.addWidget(btn_delete_points)

        btn_mass_editor = QPushButton("Mass Editor")
        btn_mass_editor.clicked.connect(self.launch_mass_editor_dialog)
        address_layout.addWidget(btn_mass_editor)

        btn_smart_split = QPushButton("Smart Split")
        btn_smart_split.clicked.connect(self.launch_smart_split_dialog)
        address_layout.addWidget(btn_smart_split)

        btn_unit_counter = QPushButton("Unit Counter")
        btn_unit_counter.clicked.connect(self.launch_unit_counter)
        address_layout.addWidget(btn_unit_counter)

        #Name each tab:
        address_tab.setLayout(address_layout)
        tab_widget.addTab(address_tab, "Address Tools")

        parcel_tab.setLayout(parcel_layout)
        tab_widget.addTab(parcel_tab, "Parcel Tools")

        other_tab.setLayout(other_layout)
        tab_widget.addTab(other_tab, "Other Tools")

        #Buttons for each parcel-related tool
        

        #Buttons for each other-related tool
        btn_batch_editor = QPushButton("Batch Field Editor")
        btn_batch_editor.clicked.connect(self.launch_batch_editor_dialog)
        other_layout.addWidget(btn_batch_editor)
        
        btn_duplicate_detector = QPushButton("Duplicate Detector")
        btn_duplicate_detector.clicked.connect(self.launch_duplicate_detector_dialog)
        other_layout.addWidget(btn_duplicate_detector)

        btn_null_orphan = QPushButton("Null + Orphan Finder")
        btn_null_orphan.clicked.connect(self.launch_null_orphan_finder_dialog)
        other_layout.addWidget(btn_null_orphan)
        
        btn_smart_snap = QPushButton("Smart Snap")
        btn_smart_snap.clicked.connect(self.launch_smart_snap_dialog)
        other_layout.addWidget(btn_smart_snap)
        
        #Apply layout to main widget
        self.main_widget.setLayout(main_layout)

    def launch_auto_address_dialog(self):
        dialog = LayerSelectionDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        parcel_name, address_name, da_name, hut_name, da_project, include_da = dialog.get_selected_options()
        try:
            added_count = process_layers(parcel_name, address_name, da_name, hut_name, da_project, include_da)
            QMessageBox.information(self, "Done", f"{added_count} new address point(s) added with full attributes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing failed:\\n{str(e)}")


    def launch_delete_points_without_external_ids_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete w/out external IDS")
        layout = QVBoxLayout()

        # Get active vector layers
        layers = QgsProject.instance().mapLayers().values()
        vector_layers = [lyr for lyr in layers if lyr.type() == lyr.VectorLayer]
        layer_names = [lyr.name() for lyr in vector_layers]

        if not layer_names:
            QMessageBox.warning(self, "No Layers", "No vector layers found.")
            return

        combo = QComboBox()
        combo.addItems(layer_names)
        layout.addWidget(QLabel("Select Address Layer:"))
        layout.addWidget(combo)

        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Delete")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def on_ok():
            selected_name = combo.currentText()
            try:
                address_layer = QgsProject.instance().mapLayersByName(selected_name)[0]
                address_layer.startEditing()
                ids_to_delete = [
                    feature.id()
                    for feature in address_layer.getFeatures()
                    if not feature['External ID'] or str(feature['External ID']).strip() == ''
                ]
                if ids_to_delete:
                    address_layer.deleteFeatures(ids_to_delete)
                address_layer.commitChanges()

                # Show result in a new dialog
                result_dialog = QDialog(self)
                result_dialog.setWindowTitle("Deletion Summary")
                result_layout = QVBoxLayout()
                result_layout.addWidget(QLabel(f"{len(ids_to_delete)} address point(s) without External ID were deleted."))
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(result_dialog.accept)
                result_layout.addWidget(close_btn)
                result_dialog.setLayout(result_layout)
                result_dialog.exec()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Deletion failed:\n{str(e)}")
            dialog.accept()

        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()

    def launch_centralize_address_points_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Centralize Address Points")
        layout = QVBoxLayout()

        # Filter only vector layers
        layers = QgsProject.instance().mapLayers().values()
        vector_layers = [lyr for lyr in layers if lyr.type() == QgsMapLayer.VectorLayer]
        layer_names = [lyr.name() for lyr in vector_layers]

        if not layer_names:
            QMessageBox.warning(self, "No Vector Layers", "No vector layers found in the project.")
            return
        # Layer dropdowns
        self.parcel_combo = QComboBox()
        self.address_combo = QComboBox()
        self.parcel_combo.addItems(layer_names)
        self.address_combo.addItems(layer_names)

        for label_text, combo in [
            ("Parcel Layer:", self.parcel_combo),
            ("Address Layer:", self.address_combo)
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addWidget(combo)
            layout.addLayout(row)

        # OK button
        ok_button = QPushButton("Centralize")
        layout.addWidget(ok_button)
        dialog.setLayout(layout)

        def on_ok_clicked():
            parcel_layer_name = self.parcel_combo.currentText()
            address_layer_name = self.address_combo.currentText()

            parcel_layer = next((lyr for lyr in vector_layers if lyr.name() == parcel_layer_name), None)
            address_layer = next((lyr for lyr in vector_layers if lyr.name() == address_layer_name), None)

            if not parcel_layer or not address_layer:
                QMessageBox.warning(dialog, "Layer Error", "Selected layers not found.")
                return

            # Build spatial index for parcels
            parcel_index = QgsSpatialIndex(parcel_layer.getFeatures())

            # Start editing address layer
            address_layer.startEditing()

            for address_feat in address_layer.getFeatures():
                address_geom = address_feat.geometry()
                if address_geom.type() != QgsWkbTypes.PointGeometry:
                    continue

                # Find intersecting parcel
                intersecting_ids = parcel_index.intersects(address_geom.boundingBox())
                for parcel_id in intersecting_ids:
                    parcel_feat = parcel_layer.getFeature(parcel_id)
                    if parcel_feat.geometry().contains(address_geom):
                        # Get centroid of parcel
                        centroid = parcel_feat.geometry().centroid().asPoint()
                        new_geom = QgsGeometry.fromPointXY(QgsPointXY(centroid))
                        address_layer.changeGeometry(address_feat.id(), new_geom)
                        break  # Stop after first match
            address_layer.commitChanges()
            QMessageBox.information(dialog, "Success", "Address points centralized.")
            dialog.accept()

        ok_button.clicked.connect(on_ok_clicked)
        dialog.exec()

    def launch_unit_counter(self):
        class UnitNumberDialog(QDialog):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Unit Counter")
                layout = QVBoxLayout()

                self.layer_combo = QComboBox()
                self.layers_dict = {}
                for layer in QgsProject.instance().mapLayers().values():
                    self.layer_combo.addItem(layer.name())
                    self.layers_dict[layer.name()] = layer

                form_layout = QFormLayout()
                self.field_input = QLineEdit("Unit Number")
                self.units_input = QLineEdit("10")
                self.floors_input = QLineEdit("4")
                self.address_input = QLineEdit()
                form_layout.addRow("Layer:", self.layer_combo)
                form_layout.addRow("Field name:", self.field_input)
                form_layout.addRow("Units per floor:", self.units_input)
                form_layout.addRow("Total floors:", self.floors_input)
                form_layout.addRow("Target ID:", self.address_input)
                layout.addLayout(form_layout)

                self.status_label = QLabel("")
                layout.addWidget(self.status_label)

                self.run_button = QPushButton("Run")
                self.run_button.clicked.connect(self.run_script)
                layout.addWidget(self.run_button)

                self.setLayout(layout)

            def run_script(self):
                layer_name = self.layer_combo.currentText()
                layer = self.layers_dict.get(layer_name)
                if layer is None:
                    self.status_label.setText(f"Layer '{layer_name}' not found.")
                    return

                field_name = self.field_input.text().strip()
                if field_name not in [f.name() for f in layer.fields()]:
                    self.status_label.setText(f"Field '{field_name}' not found in {layer_name}.")
                    return

                try:
                    units_per_floor = int(self.units_input.text())
                    total_floors = int(self.floors_input.text())
                except ValueError:
                    self.status_label.setText("Units per floor and total floors must be integers.")
                    return

                target_address = self.address_input.text().strip()
                if not target_address:
                    self.status_label.setText("Please enter a target address.")
                    return

                if not layer.isEditable():
                    if not layer.startEditing():
                        self.status_label.setText("Failed to start editing layer.")
                        return

                field_index = layer.fields().indexOf(field_name)
                count = 0

                if "ID" not in [f.name() for f in layer.fields()]:
                    self.status_label.setText("Layer does not have an 'ID' field.")
                    return

                for feature in layer.getFeatures():
                    if feature["ID"] != target_address:
                        continue
                    floor = (count // units_per_floor) + 1
                    unit_index = (count % units_per_floor) + 1
                    if floor > total_floors:
                        break
                    unit_number = f"{floor}{str(unit_index).zfill(2)}"
                    if not layer.changeAttributeValue(feature.id(), field_index, unit_number):
                        self.status_label.setText(f"Failed to update feature {feature.id()}.")
                        layer.rollBack()
                        return
                    count += 1

                if count == 0:
                    self.status_label.setText(f"No features found for address '{target_address}'.")
                    layer.rollBack()
                    return

                if layer.commitChanges():
                    self.status_label.setText(f"Updated {count} features successfully.")
                else:
                    layer.rollBack()
                    self.status_label.setText("Failed to commit changes. Rolled back edits.")

        dlg = UnitNumberDialog()
        dlg.exec()

    def launch_duplicate_detector_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Duplicate Detector")
        layout = QVBoxLayout()

        layer_combo = QComboBox()
        field_combo = QComboBox()
        layers_dict = {}

        # Populate layer combo and dictionary
        
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayerType.VectorLayer:
                layer_combo.addItem(layer.name())
                layers_dict[layer.name()] = layer


        form_layout = QFormLayout()
        form_layout.addRow("Select Layer:", layer_combo)
        form_layout.addRow("Field to Check:", field_combo)
        layout.addLayout(form_layout)

        result_list = QListWidget()
        layout.addWidget(result_list)

        run_btn = QPushButton("Detect Duplicates")
        layout.addWidget(run_btn)

        dialog.setLayout(layout)

        # Function to update field combo when layer changes
        def update_field_combo():
            layer_name = layer_combo.currentText()
            layer = layers_dict.get(layer_name)
            field_combo.clear()
            if layer:
                field_combo.addItems([f.name() for f in layer.fields()])

        layer_combo.currentIndexChanged.connect(update_field_combo)
        update_field_combo()  # Initialize field list for the first layer

        # Function to run duplicate detection
        def run_detection():
            layer_name = layer_combo.currentText()
            field_name = field_combo.currentText()
            layer = layers_dict.get(layer_name)

            if not layer or field_name not in [f.name() for f in layer.fields()]:
                QMessageBox.warning(dialog, "Invalid Input", "Please select a valid layer and field.")
                return

            value_counts = {}
            for feature in layer.getFeatures():
                value = str(feature[field_name])
                value_counts[value] = value_counts.get(value, 0) + 1

            duplicates = [val for val, count in value_counts.items() if count > 1]

            result_list.clear()
            result_list.addItem(f"Found {len(duplicates)} duplicate value(s):")
            for val in duplicates:
                result_list.addItem(f"{val} ({value_counts[val]} occurrences)")

            # Select duplicate features in the attribute table
            duplicate_ids = [feature.id() for feature in layer.getFeatures() if str(feature[field_name]) in duplicates]
            layer.selectByIds(duplicate_ids)

        run_btn.clicked.connect(run_detection)
        dialog.exec()

    def launch_smart_split_dialog(self):
        class AddressSplitterDialog(QDialog):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Smart Split")
                layout = QVBoxLayout()

                # Layer selection
                self.layer_combo = QComboBox()
                self.layers_dict = {}
                for layer in QgsProject.instance().mapLayers().values():
                    self.layer_combo.addItem(layer.name())
                    self.layers_dict[layer.name()] = layer

                form_layout = QFormLayout()
                form_layout.addRow("Layer:", self.layer_combo)

                # Address input
                self.address_input = QLineEdit()
                form_layout.addRow("Target Address:", self.address_input)

                # Homecount
                self.units_input = QLineEdit()
                self.units_input.setValidator(QIntValidator(1, 1000))
                form_layout.addRow("Number of Units:", self.units_input)

                self.field_input = QLineEdit()
                
                form_layout.addRow("Field to update:", self.field_input)


                # Style
                self.style_combo = QComboBox()
                self.style_combo.addItems([
                    "Numeric (101, 102, 103,...)",
                    "Letters (A, B, C,...)",
                    "Simple (1, 2, 3,...)"
                ])
                form_layout.addRow("Unit numbering style:", self.style_combo)

                # Offset
                self.offset_checkbox = QCheckBox("Offset points for visibility")
                self.offset_checkbox.setChecked(True)
                form_layout.addRow("", self.offset_checkbox)

                layout.addLayout(form_layout)

                # Status label
                self.status_label = QLabel("")
                layout.addWidget(self.status_label)

                self.progress_bar = QProgressBar()
                self.progress_bar.setMinimum(0)
                self.progress_bar.setMaximum(100)
                self.progress_bar.setValue(0)
                layout.addWidget(self.progress_bar)

                # Buttons
                button_layout = QHBoxLayout()
                run_button = QPushButton("Run Split")
                cancel_button = QPushButton("Cancel")
                button_layout.addWidget(run_button)
                button_layout.addWidget(cancel_button)
                layout.addLayout(button_layout)

                self.setLayout(layout)

                # Connect signals
                cancel_button.clicked.connect(self.reject)
                run_button.clicked.connect(self.run_split)
            
            def run_split(self):
                # Get the selected layer name from the combo box
                layer_name = self.layer_combo.currentText()
                layer = self.layers_dict.get(layer_name)

                # Check if the layer exists
                if layer is None:
                    self.status_label.setText(f"Layer '{layer_name}' not found.")
                    return
                
                # Get the field name input and validate it exists in the layer
                field_name = self.field_input.text().strip()
                if field_name not in [f.name() for f in layer.fields()]:
                    self.status_label.setText(f"Field '{field_name}' not found in {layer_name}.")
                    return

                # Get the target address input and validate it's not empty
                target_address = self.address_input.text().strip()
                if not target_address:
                    self.status_label.setText("Please enter a target address.")
                    return

                try:
                    units = int(self.units_input.text())
                except ValueError:
                    self.status_label.setText("Units must be a valid integer.")
                    return

                # Ensure the layer is editable
                if not layer.isEditable():
                    if not layer.startEditing():
                        self.status_label.setText("Failed to start editing layer.")
                        return

                # Get the index of the field to be updated
                field_index = layer.fields().indexOf(field_name)
                count = 0

                # Ensure the layer has an 'ID' field
                if "ID" not in [f.name() for f in layer.fields()]:
                    self.status_label.setText("Layer does not have an 'ID' field.")
                    return

                # Find the feature matching the target address
                original_feature = None
                for feature in layer.getFeatures():
                    if str(feature["ID"]).strip() == target_address:
                        original_feature = feature
                        break

                # If no matching feature is found, rollback and exit
                if original_feature is None:
                    self.status_label.setText(f"No feature found for address '{target_address}'.")
                    layer.rollBack()
                    return

                # Validate the geometry is a point
                geom = original_feature.geometry()
                if geom.isNull() or geom.type() != QgsWkbTypes.PointGeometry:
                    self.status_label.setText("Original feature does not have a valid point geometry.")
                    layer.rollBack()
                    return
                # Extract the coordinates of the original point
                point = geom.asPoint()
                x, y = point.x(), point.y()

                # Prepare to create new features
                new_features = []
                style = self.style_combo.currentText()
                offset_enabled = self.offset_checkbox.isChecked()

                for unit_index in range(1, units + 1):
                    # Generate unit number
                    if style == "Numeric (101, 102, 103,...)":
                        unit_number = str(100 + count + 1)
                    elif style == "Letters (A, B, C,...)":
                        unit_letter = chr(65 + unit_index - 1)
                        unit_number = unit_letter
                    elif style == "Simple (1, 2, 3,...)":
                        unit_number = str(unit_index)
                    else:
                        unit_number = str(unit_index)

                # Offset geometry slightly for visibility
                offset_x = x + (unit_index * 0.75 if offset_enabled else 0)
                offset_y = y + (unit_index * 0.75 if offset_enabled else 0)

                # Create a new feature with the same fields
                new_feature = QgsFeature(layer.fields())
                new_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(offset_x, offset_y)))

                # Copy attributes except 'fid', 'Vetro ID', and 'External ID'
                excluded_fields = {"fid", "vetro_id", "External ID"}
                for field in layer.fields():
                    if field.name() not in excluded_fields:
                        new_feature.setAttribute(field.name(), original_feature[field.name()])
                # Set unit number
                new_feature.setAttribute(field_name, unit_number)
                # Update 'ID' and 'Circuit ID' to include unit number
                original_id = str(original_feature["ID"]).strip()
                original_circuit_id = str(original_feature["Circuit ID"]).strip() if "Circuit ID" in [f.name() for f in layer.fields()] else ""

                new_feature.setAttribute("ID", f"{original_id} Unit {unit_number}")
                if original_circuit_id:
                    new_feature.setAttribute("Circuit ID", f"{original_circuit_id} Unit {unit_number}")
                new_features.append(new_feature)
                count += 1
                # Add new features to the layer and commit changes
                if layer.addFeatures(new_features):
                    if layer.commitChanges():
                        self.status_label.setText(f"Created {count} new unit features successfully.")
                    else:
                        layer.rollBack()
                        self.status_label.setText("Failed to commit changes. Rolled back edits.")
                else:
                    layer.rollBack()
                    self.status_label.setText("Failed to add new features.")

                    total_units = units * len(matching_features)
                    current_progress = 0

                    for original_feature in matching_features:
                        # ... (geometry and point extraction)

                        for unit_index in range(1, units + 1):
                            current_progress += 1
                            progress_percent = int((current_progress / total_units) * 100)
                            self.progress_bar.setValue(progress_percent)
                            QApplication.processEvents()  # Keeps UI responsive
        dlg = AddressSplitterDialog()
        dlg.exec()

    def launch_null_orphan_finder_dialog(self):
            class NullOrphanValidatorDialog(QDialog):
                def __init__(self):
                    super().__init__()
                    self.setWindowTitle("Null + Orphan Finder")
                    layout = QVBoxLayout()

                    # Get vector layers
                    self.layers_dict = {
                        layer.name(): layer
                        for layer in QgsProject.instance().mapLayers().values()
                        if layer.type() == QgsMapLayer.VectorLayer
                    }
                    layer_names = list(self.layers_dict.keys())

                    if not layer_names:
                        QMessageBox.warning(self, "No Layers", "No vector layers found.")
                        return

                    # Parcel and Address Layer Selection
                    self.parcel_combo = QComboBox()
                    self.address_combo = QComboBox()
                    self.parcel_combo.addItems(layer_names)
                    self.address_combo.addItems(layer_names)

                    for label_text, combo in [
                        ("Parcel Layer:", self.parcel_combo),
                        ("Address Layer:", self.address_combo)
                    ]:
                        row = QHBoxLayout()
                        row.addWidget(QLabel(label_text))
                        row.addWidget(combo)
                        layout.addLayout(row)

                    # Checkable attribute list
                    self.required_fields = [
                        "fid", "ID", "Build", "Lat", "Lon", "Assigned Resource", "Object Type", "Client", "Street Number",
                        "Street", "Unit Number", "City", "State/Province", "Postal/Zip Code", "County", "Country"
                    ]
                    self.field_list = QListWidget()
                    layout.addWidget(QLabel("Select Fields to Check for Nulls:"))
                    layout.addWidget(self.field_list)

                    for field in self.required_fields:
                        item = QListWidgetItem(field)
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.field_list.addItem(item)

                    # Run button
                    run_button = QPushButton("Run Null + Orphan Check")
                    run_button.clicked.connect(self.run_checks)
                    layout.addWidget(run_button)

                    self.setLayout(layout)

                def run_checks(self):
                    nulls = self.find_nulls()
                    orphans = self.find_orphans()

                    msg = f"Nulls found: {len(nulls)}\nOrphans found: {len(orphans)}"
                    QMessageBox.information(self, "Scan Results", msg)

                def find_nulls(self):
                    layer = self.layers_dict.get(self.address_combo.currentText())
                    if not layer:
                        return []

                    # Get checked fields
                    selected_fields = [
                        self.field_list.item(i).text()
                        for i in range(self.field_list.count())
                        if self.field_list.item(i).checkState() == Qt.CheckState.Checked
                    ]

                    if not selected_fields:
                        QMessageBox.warning(self, "No Fields Selected", "Please check at least one field.")
                        return []

                    null_features = []
                    for feature in layer.getFeatures():
                        for field in selected_fields:
                            if field not in layer.fields().names():
                                continue
                            value = feature[field]
                            if value is None or str(value).strip() == "":
                                null_features.append(feature.id())
                                break

                    if null_features:
                        layer.selectByIds(null_features)

                    return null_features

                def find_orphans(self):
                    address_layer = self.layers_dict.get(self.address_combo.currentText())
                    parcel_layer = self.layers_dict.get(self.parcel_combo.currentText())
                    if not address_layer or not parcel_layer:
                        return []
                    
                    # Build spatial index for parcel layer
                    spatial_index = QgsSpatialIndex(parcel_layer.getFeatures())
                    orphan_ids = []
                    
                    for address_feat in address_layer.getFeatures():
                        geom = address_feat.geometry()
                        if not geom:
                            continue
                        candidate_ids = spatial_index.intersects(geom.boundingBox())
                        found = False
                        for fid in candidate_ids:
                            parcel_feat = parcel_layer.getFeature(fid)
                            if parcel_feat.geometry().contains(geom):
                                found = True
                                break
                        if not found:
                            orphan_ids.append(address_feat.id())
                    if orphan_ids:
                        address_layer.selectByIds(orphan_ids)
                    return orphan_ids

            dialog = NullOrphanValidatorDialog()
            dialog.exec()

    def launch_mass_editor_dialog(self):
        class MassEditorDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Mass Editor")
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)

                # Get vector layers
                layers = QgsProject.instance().mapLayers().values()
                self.vector_layers = [lyr for lyr in layers if lyr.type() == QgsMapLayer.VectorLayer]
                layer_names = [lyr.name() for lyr in self.vector_layers]

                if not layer_names:
                    QMessageBox.warning(self, "No Vector Layers", "No vector layers found in the project.")
                    self.close()
                    return

                # Layer selection
                self.address_combo = QComboBox()
                self.address_combo.addItems(layer_names)
                
                row1 = QHBoxLayout()
                row1.addWidget(QLabel("Address Layer:"))
                row1.addWidget(self.address_combo)
                self.layout.addLayout(row1)

                # Run button
                self.run_button = QPushButton("Run")
                self.run_button.clicked.connect(self.run_editor)
                self.layout.addWidget(self.run_button)

            def run_editor(self):
                layer_name = self.address_combo.currentText()
                layer = next((lyr for lyr in self.vector_layers if lyr.name() == layer_name), None)

                if not layer:
                    QMessageBox.warning(self, "Layer Error", "Selected layer not found.")
                    return

                # Prompt for field name
                field_name, ok = QInputDialog.getText(self, "Field Name", "Enter the field name to update:")
                if not ok or not field_name:
                    return

                # Validate field
                if field_name not in [field.name() for field in layer.fields()]:
                    QMessageBox.warning(self, "Field Error", f"Field '{field_name}' not found in layer.")
                    return
                # Prompt for new value
                new_value, ok = QInputDialog.getText(self, "New Value", f"Enter new value for '{field_name}':")
                if not ok:
                    return

                # Update features
                layer.startEditing()
                for feature in layer.getFeatures():
                    layer.changeAttributeValue(feature.id(), layer.fields().indexOf(field_name), new_value)
                layer.commitChanges()

                QMessageBox.information(self, "Success", f"Field '{field_name}' updated for all features.")
        dialog = MassEditorDialog()
        dialog.exec()


    def launch_smart_snap_dialog(self):
        class SmartSnapDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Smart Snap")
                self.layout = QVBoxLayout(self)

                # Get vector layers
                layers = QgsProject.instance().mapLayers().values()
                self.vector_layers = [lyr for lyr in layers if lyr.type() == QgsMapLayer.VectorLayer]
                layer_names = [lyr.name() for lyr in self.vector_layers]

                if not layer_names:
                    QMessageBox.warning(self, "No Vector Layers", "No vector layers found in the project.")
                    self.close()
                    return

                # Layer selection
                self.line_combo = QComboBox()
                self.parcel_combo = QComboBox()
                self.line_combo.addItems(layer_names)
                self.parcel_combo.addItems(layer_names)

                for label_text, combo in [
                    ("Line Layer (to simplify):", self.line_combo),
                    ("Parcel Layer (reference):", self.parcel_combo)
                ]:
                    row = QHBoxLayout()
                    row.addWidget(QLabel(label_text))
                    row.addWidget(combo)
                    self.layout.addLayout(row)

                # Tolerance slider
                self.tolerance_slider = QSlider(Qt.Orientation.Horizontal)
                self.tolerance_slider.setMinimum(1)
                self.tolerance_slider.setMaximum(100)
                self.tolerance_slider.setValue(10)
                self.tolerance_label = QLabel("Tolerance: 1.0")
                self.tolerance_slider.valueChanged.connect(self.update_tolerance_label)

                tol_layout = QHBoxLayout()
                tol_layout.addWidget(self.tolerance_label)
                tol_layout.addWidget(self.tolerance_slider)
                self.layout.addLayout(tol_layout)

                # Angle slider
                self.angle_slider = QSlider(Qt.Orientation.Horizontal)
                self.angle_slider.setMinimum(1)
                self.angle_slider.setMaximum(45)
                self.angle_slider.setValue(5)
                self.angle_label = QLabel("Angle Threshold: 5°")
                self.angle_slider.valueChanged.connect(self.update_angle_label)

                ang_layout = QHBoxLayout()
                ang_layout.addWidget(self.angle_label)
                ang_layout.addWidget(self.angle_slider)
                self.layout.addLayout(ang_layout)

                # Preview checkbox
                self.preview_checkbox = QCheckBox("Enable Preview")
                self.preview_checkbox.setToolTip("Enable preview mode to visualize changes before applying.")
                self.preview_checkbox.stateChanged.connect(self.toggle_preview)
                self.layout.addWidget(self.preview_checkbox)

                # Run button
                run_button = QPushButton("Run")
                run_button.setToolTip("Click to apply snapping and simplification to the line layer.")
                run_button.clicked.connect(self.run_snap)
                self.layout.addWidget(run_button)

            def update_tolerance_label(self, value):
                self.tolerance_label.setText(f"Tolerance: {value / 10:.1f}")
                if self.preview_checkbox.isChecked():
                    self.toggle_preview(Qt.CheckState.Checked)

            def update_angle_label(self, value):
                self.angle_label.setText(f"Angle Threshold: {value}°")
                if self.preview_checkbox.isChecked():
                    self.toggle_preview(Qt.CheckState.Checked)

            def toggle_preview(self, state):
                self.remove_preview_layer()
                if state == Qt.CheckState.Checked:
                    self.show_preview()

            def show_preview(self):
                line_layer_name = self.line_combo.currentText()
                parcel_layer_name = self.parcel_combo.currentText()

                line_layer = next((lyr for lyr in self.vector_layers if lyr.name() == line_layer_name), None)
                parcel_layer = next((lyr for lyr in self.vector_layers if lyr.name() == parcel_layer_name), None)

                if not line_layer or not parcel_layer:
                    QMessageBox.warning(self, "Layer Error", "Selected layers not found.")
                    return

                crs = line_layer.crs().authid()
                preview_layer = QgsVectorLayer(f"LineString?crs={crs}", "Simplified Preview", "memory")
                prov = preview_layer.dataProvider()

                for feat in line_layer.getFeatures():
                    geom = feat.geometry()
                    simplified_geom = self.get_simplified_geometry(geom, parcel_layer)
                    new_feat = QgsFeature()
                    new_feat.setGeometry(simplified_geom)
                    prov.addFeature(new_feat)

                QgsProject.instance().addMapLayer(preview_layer)
                self.preview_layer = preview_layer

            def remove_preview_layer(self):
                if hasattr(self, 'preview_layer'):
                    QgsProject.instance().removeMapLayer(self.preview_layer.id())
                    del self.preview_layer

            def run_snap(self):
                line_layer_name = self.line_combo.currentText()
                parcel_layer_name = self.parcel_combo.currentText()

                line_layer = next((lyr for lyr in self.vector_layers if lyr.name() == line_layer_name), None)
                parcel_layer = next((lyr for lyr in self.vector_layers if lyr.name() == parcel_layer_name), None)

                if not line_layer or not parcel_layer:
                    QMessageBox.warning(self, "Layer Error", "Selected layers not found.")
                    return

                line_layer.startEditing()
                for feat in line_layer.getFeatures():
                    geom = feat.geometry()
                    simplified_geom = self.get_simplified_geometry(geom, parcel_layer)
                    if simplified_geom and not simplified_geom.equals(geom):
                        line_layer.changeGeometry(feat.id(), simplified_geom)
                        print(f"Updated geometry for feature {feat.id()}")
                    else:
                        print(f"No change for feature {feat.id()}")

                line_layer.commitChanges()
                QMessageBox.information(self, "Success", "Line layer vertices snapped to parcel layer and simplified.")
                self.remove_preview_layer()

            def get_simplified_geometry(self, geom, reference_layer):
                tolerance = self.tolerance_slider.value() / 10.0
                angle_threshold = self.angle_slider.value()

                def angle_between(p1, p2, p3):
                    a = QgsPointXY(p1.x() - p2.x(), p1.y() - p2.y())
                    b = QgsPointXY(p3.x() - p2.x(), p3.y() - p2.y())
                    dot = a.x() * b.x() + a.y() * b.y()
                    mag_a = math.hypot(a.x(), a.y())
                    mag_b = math.hypot(b.x(), b.y())
                    if mag_a == 0 or mag_b == 0:
                        return 180
                    cos_angle = dot / (mag_a * mag_b)
                    cos_angle = max(min(cos_angle, 1), -1)
                    return math.degrees(math.acos(cos_angle))

                def find_nearest_vertex(pt, ref_layer):
                    min_dist = float('inf')
                    closest_pt = pt
                    for ref_feat in ref_layer.getFeatures():
                        ref_geom = ref_feat.geometry()
                        result = ref_geom.closestVertex(QgsPointXY(pt))
                        if result[0] != -1:
                            candidate_pt = result[1]
                            dist = math.hypot(pt.x() - candidate_pt.x(), pt.y() - candidate_pt.y())
                            if dist < min_dist:
                                min_dist = dist
                                closest_pt = candidate_pt
                    return closest_pt, min_dist

                if geom.type() != QgsWkbTypes.LineGeometry:
                    return geom  # Skip non-line geometries

                if geom.isMultipart():
                    lines = geom.asMultiPolyline()
                else:
                    lines = [geom.asPolyline()]

                new_lines = []
                for line in lines:
                    simplified_line = []
                    for i, pt in enumerate(line):
                        snapped_pt, dist = find_nearest_vertex(pt, reference_layer)
                        if dist < tolerance:
                            pt = snapped_pt

                        if 0 < i < len(line) - 1:
                            ang = angle_between(line[i - 1], pt, line[i + 1])
                            if ang < angle_threshold:
                                continue

                        simplified_line.append(pt)

                    if len(simplified_line) >= 2:
                        new_lines.append(simplified_line)

                if geom.isMultipart():
                    return QgsGeometry.fromMultiPolylineXY(new_lines)
                else:
                    return QgsGeometry.fromPolylineXY(new_lines[0])

        dialog = SmartSnapDialog()
        dialog.exec()

    def launch_batch_editor_dialog(self):
        class BatchFieldEditorDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Batch Field Editor")
                self.layout = QVBoxLayout(self)

                # Get vector layers
                layers = QgsProject.instance().mapLayers().values()
                self.vector_layers = [lyr for lyr in layers if lyr.type() == QgsMapLayer.VectorLayer]
                layer_names = [lyr.name() for lyr in self.vector_layers]

                if not layer_names:
                    QMessageBox.warning(self, "No Vector Layers", "No vector layers found in the project.")
                    self.close()
                    return

                # Layer selection
                self.layer_combo = QComboBox()
                self.layer_combo.addItems(layer_names)

                for label_text, combo in [
                    ("Layer:", self.layer_combo)
                ]:
                    row = QHBoxLayout()
                    row.addWidget(QLabel(label_text))
                    row.addWidget(combo)
                    self.layout.addLayout(row)

                # Run button
                self.run_button = QPushButton("Run")
                self.run_button.clicked.connect(self.run_editor)
                self.layout.addWidget(self.run_button)
            def run_editor(self):
                layer_name = self.layer_combo.currentText()
                layer = next((lyr for lyr in self.vector_layers if lyr.name() == layer_name), None)

                if not layer:
                    QMessageBox.warning(self, "Layer Error", "Selected layer not found.")
                    return

                # Prompt for field name
                field_name, ok = QInputDialog.getText(self, "Field Name", "Enter the field name to update:")
                if not ok or not field_name:
                    return

                # Validate field
                if field_name not in [field.name() for field in layer.fields()]:
                    QMessageBox.warning(self, "Field Error", f"Field '{field_name}' not found in layer.")
                    return
                # Prompt for new value
                new_value, ok = QInputDialog.getText(self, "New Value", f"Enter new value for '{field_name}':")
                if not ok:
                    return

                # Update features
                layer.startEditing()
                for feature in layer.getFeatures():
                    layer.changeAttributeValue(feature.id(), layer.fields().indexOf(field_name), new_value)
                layer.commitChanges()

                QMessageBox.information(self, "Success", f"Field '{field_name}' updated for all features.")
        dialog = BatchFieldEditorDialog()
        dialog.exec()

    def launch_generic_dialog(self, title):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        self.layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        dialog.setLayout(layout)
        dialog.exec()
