# 3D Slicer Uncertainty Visualizer

A 3D Slicer module for visualizing structure-wise uncertainty of vessels segmented by a deep learning model. The functionality involves adding, deleting, and viewing individual components based on their uncertainty values.

## Installation and Setup

### Prerequisites
- 3D Slicer installed on your system

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/3d-slicer-uncertainty-visualizer.git
   ```

2. **Enable Developer Mode**
   - Go to **Slicer menu** → **Edit** → **Application Settings** → **Developer**
   - Check **"Enable Developer Mode"**

3. **Load the Extension**
   - Navigate to **Modules** → **Developer Tools** → **Extension Wizard**
   - Click **'Select Extension'**
   - Select the root folder of this GitHub repository
   - Select **New** as the module to load

4. **Access the Module**
   - Once the extension and module load successfully, go to **Modules** → **Examples** → **New**

## Usage Instructions

### Required Files
Before clicking **"Generate Uncertainty Map"**, ensure you have loaded these 3 files as **Volumes**:

1. **Uncertainty File**
   - Rename this file following the pattern: `*uncertainty_file*` before loading
   - Load as Volume (use the float volume, not the int version)

2. **Segmentation File** 
   - Rename this file following the pattern: `*segmentation_file*` before loading
   - Load as Volume

3. **Image File**
   - Load for visualization purposes

> **Important:** Make sure no other files are loaded in Slicer that follow the above naming patterns.

### Getting Started
1. Click the **"Generate Uncertainty Map"** button to begin working
2. The **'View'** button for the 4th view (3D render) only works when the 4th view is in full screen mode

## Development Notes
- Most of the code is located in `New.py`

## Video Demonstrations

### [YouTube] Our 3D Slicer plug-in video demo
[![Watch on YouTube](https://img.youtube.com/vi/PB7xBGxw5iU/hqdefault.jpg)](https://youtu.be/PB7xBGxw5iU)

### [YouTube] 3D Slicer standard proof-reading tools' video demo
[![Watch on YouTube](https://img.youtube.com/vi/MJFCrtKqvK8/hqdefault.jpg)](https://youtu.be/MJFCrtKqvK8)

## Related repositories:
- Official 2D: https://github.com/Saumya-Gupta-26/struct-uncertainty.git
- Official 3D: https://github.com/Saumya-Gupta-26/struct-uncertainty-3D.git
