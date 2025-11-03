def delete_points_without_external_ids(self):
    dialog = QDialog(self)
    dialog.setWindowTitle("Select Address Layer")
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
