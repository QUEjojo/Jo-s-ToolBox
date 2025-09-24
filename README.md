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
- Select a tool from the dropdown menu:
  - Auto Address Creator
  - Delete Points Without External IDs
  - Centralize Address Points
  - Unit Counter
  - Duplicate Detector
- Click the **"Click Me"** button to execute the selected tool.

## Features
### 1. Auto Address Creator
Automatically generates address attributes for selected point features.

### 2. Delete Points Without External IDs
Removes address points that lack external identifiers, ensuring data integrity.

### 3. Centralize Address Points
Adjusts address points to be centered within their corresponding parcel or building footprint.

### 4. Unit Counter
Counts the number of residential or commercial units within a selected area.

### 5. Duplicate Detector
Identifies and flags duplicate address points based on spatial and attribute criteria.

## Contributing
Contributions are welcomed! To contribute:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m "Add feature"`
4. Push to your branch: `git push origin feature-name`
5. Submit a pull request.

## License
License= MIT

##Contact
For questions or suggestions, please contact [Jovita(Jo)] at [gomezjovita68@gmail.com].
