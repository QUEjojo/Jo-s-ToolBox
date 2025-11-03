# joTOOLS for QGIS

## Overview
joTOOLS is a versatile QGIS plugin designed to streamline common geospatial data tasks. It provides a user-friendly dock panel interface with multiple tools to manage and analyze address point data efficiently.

## Installation
1. Clone or download this repository.
2. Copy the plugin folder into your QGIS plugins directory:
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   - **macOS/Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
3. Launch QGIS and enable the plugin via **Plugins > Manage and Install Plugins**.

## Usage
Once installed and activated:
- The plugin appears as a dock panel titled **joTOOLS**.
- Select the Tool Tab depending on what you want layer you're working with.
 - Address Tools:
  - Auto Address Creator
  - Centralize Address Points
  - Delete Points without External IDs
  - Mass Editor
  - Unit Counter
 - Parcel Tools:
  - NA
 - Other Tools:
  - Batch Field Editor
  - Duplicate Detector
  - Null + Orphan Finder
  - Smart Snap
- Click the **"Run"** button to execute the selected tool.

## Features
### 1. Auto Address Creator
Automatically generates address attributes for selected point features.

### 2. Centralize Address Points
Adjusts address points to be centered within their corresponding parcel or building footprint.

### 3. Delete Points Without External IDs
Removes address points that lack external identifiers, ensuring data integrity.

### 4. Mass Editor
Updates a given attribute field value for selected features in selected layer.

### 5. Smart Split
Automatically splits an address point into multiple sub-features based on the Homecount attribute.

### 6. Unit Counter
Counts the number of residential or commercial units within a selected area.

### 7. Batch Field Editor
Updates multiple fields across selected features within any layer.

### 8. Duplicate Detector
Identifies and flags duplicate address points based on spatial and attribute criteria.

### 9. Null + Orphan Finder
Detects address points missing essential fields, and detects orphaned features (points not linked to a parent feature, such as a parcel, building footprint, or street).

### 10. Smart Snap
Automatically detects and snaps nearby vertices within a configurable tolerance to reduce redundant geometry complexity, making maps render faster and look cleaner, while maintaining spatial integrity.

## Contributing
Contributions are welcomed! To contribute:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m "Add feature"`
4. Push to your branch: `git push origin feature-name`
5. Submit a pull request.

## License
license=MIT

##Contact
For questions or suggestions, please contact [Jovita(Jo)] at [gomezjovita68@gmail.com].
