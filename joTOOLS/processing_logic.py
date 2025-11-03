from qgis.core import (
    QgsProject,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsSpatialIndex,
    QgsWkbTypes
)

def process_layers(parcel_name, address_name, da_name, hut_name, da_project="", include_da=True):
    project = QgsProject.instance()
    
    parcel_layer = project.mapLayersByName(parcel_name)[0]
    address_layer = project.mapLayersByName(address_name)[0]
    
    da_layers = project.mapLayersByName(da_name)
    if include_da and da_layers:
        da_layer = da_layers[0]
        da_index = QgsSpatialIndex(da_layer.getFeatures())
    else:
        da_layer = None
        da_index = None

    # Required fields
    required_fields = {
        'ID': str,
        'Street Number': str,
        'Street': str,
        'Postal/Zip Code': str,
        'Lat': float,
        'Lon': float,
        'City': str,
        'Assigned Resource': str,
        'Client': str,
        'OLT Name': str,
        'Construction Area': str,
        'COS Object Group': str,
        'State/Province': str,
        'County': str,
        'Country': str,
        'COS Object Status': str,
        'OSP Deployment Status': str,
        'Right of Entry': str,
        'Contract Target Address?': str,
        'Object Type': str,
        'Build': str,
        'DA': str,
        'FDH': str,
        'Circuit ID': str
    }

    # Add missing fields
    field_names = [field.name() for field in address_layer.fields()]
    new_fields = [QgsField(name, type_) for name, type_ in required_fields.items() if name not in field_names]
    if new_fields:
        address_layer.dataProvider().addAttributes(new_fields)
        address_layer.updateFields()

    field_indices = {name: address_layer.fields().indexOf(name) for name in required_fields.keys()}

    landuse_map = {
        'Commercial': 'COM',
        'Government': 'GOV',
        'HOA': 'HOA',
        'Multiple Business': 'MBU',
        'Mixed Use': 'MXU',
        'Other': 'OTHER',
        'Deselected': 'OTHER',
        'Religious': 'REL',
        'Single-Family': 'SFU',
        'Vacant': 'VAC',
        'Multi-Family': 'MDU'
    }

    address_index = QgsSpatialIndex(address_layer.getFeatures())
    da_index = QgsSpatialIndex(da_layer.getFeatures())

    address_layer.startEditing()
    added_count = 0

    for parcel_feat in parcel_layer.getFeatures():
        parcel_geom = parcel_feat.geometry()
        if parcel_geom.type() != QgsWkbTypes.PolygonGeometry or parcel_geom.isEmpty():
            continue

        possible_ids = address_index.intersects(parcel_geom.boundingBox())
        has_address = any(parcel_geom.contains(address_layer.getFeature(addr_id).geometry()) for addr_id in possible_ids)

        if not has_address:
            centroid = parcel_geom.centroid()
            if not centroid or centroid.isEmpty():
                continue


        if include_da:
                da_layer = project.mapLayersByName(da_name)[0]
                da_index = QgsSpatialIndex(da_layer.getFeatures())
        else:
            da_layer = None
            da_index = None
        
        if include_da:
            # DA-related logic
            centroid_geom = QgsGeometry.fromPointXY(centroid.asPoint())
            da_ids = da_index.intersects(centroid_geom.boundingBox())
            da_value = None
            inside_da = False

            for da_id in da_ids:
                da_feat = da_layer.getFeature(da_id)
                if da_feat.geometry().contains(centroid_geom) and da_feat['Project'] == da_project:
                    da_value = da_feat['Project']
                    inside_da = True
                    break

            if not inside_da:
                continue
        else:
            da_value = None
            inside_da = True

            

            new_feat = QgsFeature(address_layer.fields())
            new_feat.setGeometry(centroid_geom)
            attrs = [None] * len(address_layer.fields())

            full_address = parcel_feat['PAR_ADDR1']
            if full_address:
                attrs[field_indices['ID']] = full_address
                parts = full_address.strip().split(' ', 1)
                if len(parts) > 0:
                    attrs[field_indices['Street Number']] = parts[0]
                if len(parts) > 1:
                    attrs[field_indices['Street']] = parts[1]

            attrs[field_indices['Postal/Zip Code']] = parcel_feat['PAR_ZIP']
            attrs[field_indices['Lat']] = centroid_geom.asPoint().y()
            attrs[field_indices['Lon']] = centroid_geom.asPoint().x()
            attrs[field_indices['City']] = parcel_feat['MUNI']
            attrs[field_indices['Assigned Resource']] = 'CNS'
            attrs[field_indices['Client']] = 'BSN'
            attrs[field_indices['OLT Name']] = hut_name
            attrs[field_indices['Construction Area']] = hut_name
            attrs[field_indices['COS Object Group']] = 'default'
            attrs[field_indices['State/Province']] = 'TN'
            attrs[field_indices['County']] = 'SHELBY'
            attrs[field_indices['Country']] = 'US'
            attrs[field_indices['COS Object Status']] = 'Not deliverable'
            attrs[field_indices['OSP Deployment Status']] = 'Planned'
            attrs[field_indices['Right of Entry']] = 'Not Required'
            attrs[field_indices['Contract Target Address?']] = 'UNK'

            # OLT Name and Construction Area
            olt_suffix = ''.join(filter(str.isdigit, hut_name))
            olt_name = f"tn-mem.hut.MEM{olt_suffix.zfill(2)}" if olt_suffix else "tn-mem.hut.UNKNOWN"
            attrs[field_indices['OLT Name']] = olt_name
            attrs[field_indices['Construction Area']] = hut_name


            landuse_value = parcel_feat['LANDUSE']
            normalized = landuse_value.strip().lower() if landuse_value else ''
            object_type = next((abbrev for key, abbrev in landuse_map.items() if key.lower() in normalized), 'OTHER')
            attrs[field_indices['Object Type']] = object_type
            attrs[field_indices['Build']] = 'No' if object_type in ['MDU', 'MBU', 'HOA'] else 'Yes'
            attrs[field_indices['DA']] = da_value
            attrs[field_indices['FDH']] = da_value

            if da_value and full_address:
                circuit_id = f"{da_value}.{full_address.replace(' ', '.')}"
                attrs[field_indices['Circuit ID']] = circuit_id

            new_feat.setAttributes(attrs)
            address_layer.addFeature(new_feat)
            added_count += 1

    address_layer.commitChanges()
    return added_count
