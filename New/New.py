import logging
import os
from typing import Annotated, Optional

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode


#
# New
#

import subprocess

try:
    import SimpleITK as sitk 
except ModuleNotFoundError:
    subprocess.check_call(["pip", "install", "SimpleITK"])
    import SimpleITK as sitk 

try:
    import numpy as np
except ModuleNotFoundError:
    subprocess.check_call(["pip", "install", "numpy"])
    import numpy as np

try:
    import matplotlib.pyplot as plt
    # import matplotlib
except ModuleNotFoundError:
    subprocess.check_call(["pip3", "install", "matplotlib"])
    import matplotlib.pyplot as plt
    # import matplotlib

try:
    import cc3d
except ModuleNotFoundError:
    subprocess.check_call(["pip", "install", "connected-components-3d"])
    import cc3d

import qt
import SegmentStatistics
import os
from pathlib import Path
import sys

script_dir = Path(__file__).resolve().parent
parent_dir = Path(script_dir).parent
saved_dir = Path(parent_dir) / "saved_files/"
saved_dir.mkdir(parents=True, exist_ok=True)

class New(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "New"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#New">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # New1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='New',
        sampleName='New1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'New1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='New1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='New1'
    )

    # New2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='New',
        sampleName='New2',
        thumbnailFileName=os.path.join(iconsPath, 'New2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='New2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='New2'
    )


#
# NewParameterNode
#

@parameterNodeWrapper
class NewParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """
    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# NewWidget
#

class NewWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

        self.label_values = []
        self.display_label_values = []
        self.added_uncertainties = []
        self.deleted_uncertainties = []
        self.connected_components = None
        self.total_components = None
        self.uncertainty_float_node = None
        self.uncertainty_int_node = None
        self.predict_node = None
        self.colors = None
        self.opaque = None

        self.image_origin = None
        self.image_spacing = None
        self.image_direction = None

    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        # uiWidget = slicer.util.loadUI(self.resourcePath('UI/TestGrid.ui'))
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/New1.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = NewLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

        # label_values = ["0.1", "0.2", "0.3", "0.4", "0.5","0.1", "0.2", "0.3", "0.4", "0.5","0.1", "0.2", "0.3", "0.4", "0.5","0.1", "0.2", "0.3", "0.4", "0.5","0.1", "0.2", "0.3", "0.4", "0.5",]  # Replace with your list of label values
        # label_values = []
        self.createDynamicGrid(self.label_values)

    def createDynamicGrid(self, label_values):
        dynamicGridFrame = self.ui.dynamicGridFrame

        # Remove existing layout if any
        while dynamicGridFrame.layout():
            item = dynamicGridFrame.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Create a new container widget for the dynamic grid
        container_widget = qt.QWidget(dynamicGridFrame)
        grid_layout = qt.QGridLayout(container_widget)

        # Add static "Generate Uncertainty Map" button to the first row
        generateMapButton = qt.QPushButton("Generate Uncertainty Map", container_widget)
        generateMapButton.setEnabled(False if label_values else True)
        grid_layout.addWidget(generateMapButton, 0, 0, 1, 4)  # Span the entire row
        generateMapButton.connect('clicked(bool)', self.onGenerateMapButtonClicked)

        slider = qt.QSlider(qt.Qt.Horizontal, container_widget)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(100)
        slider.setSingleStep(1)  # Set the step to 1
        slider.setPageStep(10)   # Set the page step to 10 for larger increments
        slider.setTickInterval(10)  # Set tick interval for better visualization
        slider.setTickPosition(qt.QSlider.TicksBelow)  # Set tick position

        tick_labels = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
        # for i, label in enumerate(tick_labels):
        #     slider.setTickLabel(i * 10, label)

        grid_layout.addWidget(slider, 1, 0, 1, 4)
        slider.connect('valueChanged(int)', lambda value: self.onSliderValueChanged(value / 100.0))

        # if label_values:
        #     print("here")
        #     slider = qt.QSlider(qt.Qt.Horizontal, container_widget)
        #     slider.setMinimum(0)
        #     slider.setMaximum(100)
        #     slider.setValue(50)
        #     grid_layout.addWidget(slider, 1, 0, 1, 4)  
        #     slider.connect('valueChanged(int)', self.onSliderValueChanged)

        for row, (label, label_value, voxel_count, bounding_box, segment_name) in enumerate(label_values):
            my_label = qt.QLabel("Uncertainty: {} ({}) ({})".format(label_value,voxel_count,label) , container_widget)
            # my_label.setStyleSheet("background-color: lightblue;")
            # my_label.setStyleSheet("background-color: rgb({}, {}, {});".format(self.colors[label-1][0]*255, self.colors[label-1][1]*255, self.colors[label-1][2]*255))
            my_label.setStyleSheet("background-color: rgb({}, {}, {});".format(self.colors[row][0]*255, self.colors[row][1]*255, self.colors[row][2]*255))

            # Create three buttons for each row
            view_button = qt.QPushButton(f"View {label}", container_widget)
            add_button = qt.QPushButton(f"Add {label}", container_widget)
            delete_button = qt.QPushButton(f"Delete {label}", container_widget)

            # Add buttons and label to the grid layout
            grid_layout.addWidget(my_label, row + 2, 0)
            grid_layout.addWidget(view_button, row + 2, 1)
            grid_layout.addWidget(add_button, row + 2, 2)
            grid_layout.addWidget(delete_button, row + 2, 3)

            # Connect buttons to corresponding functions
            view_button.connect('clicked(bool)', lambda _, row=row, label=label, value=label_value, bounding_box=bounding_box, segment_name=segment_name: self.onViewButtonClicked(row, label, value, bounding_box,segment_name))
            add_button.connect('clicked(bool)', lambda _, row=row, label=label, value=label_value, segment_name=segment_name: self.onAddButtonClicked(row, label, value, segment_name))
            delete_button.connect('clicked(bool)', lambda _, row=row, label=label, value=label_value, segment_name=segment_name: self.onDeleteButtonClicked(row, label, value, segment_name))

        if label_values:
            saveButton = qt.QPushButton("Save Changes", container_widget)
            saveButton.setEnabled(True if (self.added_uncertainties or self.deleted_uncertainties) else False)
            grid_layout.addWidget(saveButton, len(label_values)+1, 0, 1, 4)  # Span the entire row
            saveButton.connect('clicked(bool)', self.onSaveButtonClicked)

        if self.added_uncertainties:
            my_label = qt.QLabel("Added Uncertainties List: ", container_widget)
            grid_layout.addWidget(my_label, len(label_values)+2 , 0,1,4)
            for row, (label, label_value, voxel_count, bounding_box, segment_name) in enumerate(self.added_uncertainties):
                my_label = qt.QLabel("{}) {} ({}) ({}))".format(row+1, label_value, voxel_count, label), container_widget)
                grid_layout.addWidget(my_label, len(label_values)+3 + row , 0,1,4)

        if self.deleted_uncertainties:
            my_label = qt.QLabel("Deleted Uncertainties List: ", container_widget)
            grid_layout.addWidget(my_label, len(label_values)+3+len(self.added_uncertainties) , 0,1,4)
            for row, (label, label_value, voxel_count, bounding_box, segment_name) in enumerate(self.deleted_uncertainties):
                my_label = qt.QLabel("{}) {} ({}) ({}))".format(row+1, label_value, voxel_count, label), container_widget)
                grid_layout.addWidget(my_label, len(label_values)+4+len(self.added_uncertainties) + row , 0,1,4)

        # Set the new container widget as the layout for dynamicGridFrame
        dynamicGridFrame.setLayout(qt.QVBoxLayout())
        dynamicGridFrame.layout().addWidget(container_widget)

    def calculateCenter(self, slice):
        return (slice.stop + slice.start) / 2.0

    def calculateCenterAndExtent(self, slice):
        center = (slice.start + slice.stop) / 2.0
        extent = slice.stop - slice.start
        return center, extent


    def zoomToSegment(self, segmentationNode, segmentID):
        segment = segmentationNode.GetSegmentation().GetSegment(segmentID)
        if not segment:
            print("Segment not found")
            return

        # Calculate the bounding box of the segment
        bounds = [0, -1, 0, -1, 0, -1]
        segmentationNode.GetSegmentation().GetSegment(segmentID).GetBounds(bounds)
        if bounds == [0, -1, 0, -1, 0, -1]:
            print("Bounds not found")
            return

        # Calculate the center and the range of the bounding box
        center = [(bounds[0]+bounds[1])/2, (bounds[2]+bounds[3])/2, (bounds[4]+bounds[5])/2]
        range = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
        maxRange = max(range)

        # Adjust the 3D view camera to focus on the segment
        layoutManager = slicer.app.layoutManager()
        for i in range(layoutManager.threeDViewCount()):
            threeDView = layoutManager.threeDWidget(i).threeDView()
            camera = threeDView.mrmlViewNode().GetActiveCameraNode().GetCamera()
            camera.SetPosition(center[0], center[1], center[2] + maxRange * 1.5)
            camera.SetFocalPoint(center)
            camera.SetViewUp(0, 1, 0)
            threeDView.resetFocalPoint()


    def createLabelMapVolumeNode(self):
        # Convert the connected components array to a SimpleITK image
        labelMapSitk = sitk.GetImageFromArray(self.connected_components.astype(np.int16))
        labelMapSitk.SetOrigin((0.0, 0.0, 0.0))  # Set the origin
        # labelMapSitk.SetSpacing((1.0, 1.0, 1.0))  # Set the spacing
        labelMapSitk.SetSpacing((0.82421875, 0.82421875, 1.0))
        labelMapSitk.SetDirection((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))


        # Create a new label map volume node
        labelMapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        slicer.util.updateVolumeFromArray(labelMapNode, self.connected_components)

        # Return the created node
        return labelMapNode


    def onSliderValueChanged(self, new_value):
        print("new_value",new_value)
        # for row, (label, label_value, voxel_count, bounding_box, segment_name) in enumerate(label_values):

        # self.display_label_values = list(filter(lambda x: float(x[1])<=new_value, self.label_values))
        # unfiltered_values = [x for x in self.label_values if not float(x[1])<=new_value]

        filtered_values = []
        # unfiltered_values = []
        for i in self.label_values:
            if float(i[1])<=new_value:
                filtered_values.append(i)
                segNode = slicer.util.getNode(i[4])
                segNode.GetDisplayNode().SetVisibility(True)
            else:
                # unfiltered_values.append(i)
                segNode = slicer.util.getNode(i[4])
                segNode.GetDisplayNode().SetVisibility(False)

        self.display_label_values = filtered_values
        # self.createDynamicGrid(self.display_label_values)
        # self.createDynamicGrid(self.label_values)

    def onViewButtonClicked(self, row, label, value, bounding_box, segment_name):
        print(f"View button clicked for row {row} label {label} and value: {value} for segment: {segment_name}")

        # # Your bounding box slices
        # # xSlice, ySlice, zSlice = (slice(0, 331, None), slice(0, 512, None), slice(0, 512, None))
        # xSlice, ySlice, zSlice = bounding_box[0], bounding_box[1], bounding_box[2]

        # # Calculate the center of each slice
        # xCenter = self.calculateCenter(xSlice)
        # yCenter = self.calculateCenter(ySlice)
        # zCenter = self.calculateCenter(zSlice)

        # # # Calculate the center and extent for each slice
        # # xCenter, xExtent = self.calculateCenterAndExtent(xSlice)
        # # yCenter, yExtent = self.calculateCenterAndExtent(ySlice)
        # # zCenter, zExtent = self.calculateCenterAndExtent(zSlice)


        # # Get the slice nodes for Red, Yellow, and Green views
        # redSlice = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
        # yellowSlice = slicer.app.layoutManager().sliceWidget("Yellow").mrmlSliceNode()
        # greenSlice = slicer.app.layoutManager().sliceWidget("Green").mrmlSliceNode()


        # # zoomFactor = 1.0
        # # redSlice.SetFieldOfView(zExtent * zoomFactor, zExtent * zoomFactor, 1)
        # # yellowSlice.SetFieldOfView(xExtent * zoomFactor, xExtent * zoomFactor, 1)
        # # greenSlice.SetFieldOfView(yExtent * zoomFactor, yExtent * zoomFactor, 1)


        # # Set the slice offset for each view to center on the bounding box
        # redSlice.SetSliceOffset(zCenter)
        # yellowSlice.SetSliceOffset(xCenter)
        # greenSlice.SetSliceOffset(yCenter)

        # segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
        # segmentID = "Segment_12"  # replace with your segment ID
        # self.zoomToSegment(segmentationNode, segmentID)





        # self.adjustViewsToBoundingBox((slice(0, 331, None), slice(0, 512, None), slice(0, 512, None)))
        # self.adjustViewsToBoundingBox(bounding_box)



# here
        # segNode = slicer.util.getNode(segment_name)
        # segNode.GetDisplayNode().SetVisibility(not bool(segNode.GetDisplayNode().GetVisibility()))
# till here
        
        if self.opaque:
            try:
                segNode = slicer.util.getNode(self.opaque)
                segNode.GetDisplayNode().SetOpacity(0.2)
            except Exception as e:
                print("\n\n\n\n\n\n\n\n\n\n\ne:",e)            
                
        segNode = slicer.util.getNode(segment_name)
        segNode.GetDisplayNode().SetOpacity(1)
        self.opaque = segment_name

        segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
        segStatLogic.getParameterNode().SetParameter("Segmentation", segNode.GetID())
        segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.centroid_ras.enabled", str(True))
        segStatLogic.computeStatistics()
        stats = segStatLogic.getStatistics()

        # pointListNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
        # pointListNode.SetName("My_markup_My_Segment_188")
        # pointListNode.CreateDefaultDisplayNodes()
        for segmentId in stats["SegmentIDs"]:
          centroid_ras = stats[segmentId,"LabelmapSegmentStatisticsPlugin.centroid_ras"]
          # segmentName = segNode.GetSegmentation().GetSegment(segmentId).GetName()
          # pointListNode.AddFiducialFromArray(centroid_ras, segmentName)
        slicer.modules.markups.logic().JumpSlicesToLocation(centroid_ras[0], centroid_ras[1], centroid_ras[2], True)
    
    def adjustViewsToBoundingBox(self, bounding_box):
        # Extract the min and max coordinates of the bounding box
        minX, maxX = bounding_box[0].start, bounding_box[0].stop
        minY, maxY = bounding_box[1].start, bounding_box[1].stop
        minZ, maxZ = bounding_box[2].start, bounding_box[2].stop

        # Calculate the center of the bounding box
        centerX = (minX + maxX) / 2.0
        centerY = (minY + maxY) / 2.0
        centerZ = (minZ + maxZ) / 2.0

        # Get the slice nodes for each view
        redSliceNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
        yellowSliceNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
        greenSliceNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')

        # Adjust the slice nodes to center on the bounding box
        redSliceNode.JumpSlice(centerX, centerY, centerZ)
        yellowSliceNode.JumpSlice(centerX, centerY, centerZ)
        greenSliceNode.JumpSlice(centerX, centerY, centerZ)

        # Optional: Adjust the field of view to fit the bounding box size
        fovX = maxX - minX
        fovY = maxY - minY
        fovZ = maxZ - minZ
        maxFov = max(fovX, fovY, fovZ)
        redSliceNode.SetFieldOfView(maxFov, maxFov, 1)
        yellowSliceNode.SetFieldOfView(maxFov, maxFov, 1)
        greenSliceNode.SetFieldOfView(maxFov, maxFov, 1)

        # Update the views
        slicer.app.processEvents()






    def onAddButtonClicked(self, row, label, value, segment_name):
        print(f"Add button clicked for row {row} label {label} and value: {value}")
        extracted_image = self.connected_components * (self.connected_components == label)
        self.predict_node_array[extracted_image == label] = 1
        # self.added_uncertainties.append(self.label_values.pop(row))
        self.added_uncertainties.append(self.label_values.pop(row))

        segNode = slicer.util.getNode(segment_name)
        segNode.GetDisplayNode().SetVisibility(True)
        segNode.GetDisplayNode().SetOpacity(0.2)
        if self.opaque == segment_name:
            self.opaque = None
        else:
            print('\n\n\n\n\n in add function', self.opaque, segment_name)

        slicer.util.updateVolumeFromArray(self.predict_node, self.predict_node_array)
        self.createDynamicGrid(self.label_values)


    def onDeleteButtonClicked(self, row, label, value, segment_name):
        print(f"Delete button clicked for row {row} label {label} and value: {value}")
        extracted_image = self.connected_components * (self.connected_components == label)
        self.predict_node_array[extracted_image == label] = 0
        # self.deleted_uncertainties.append(self.label_values.pop(row))
        self.deleted_uncertainties.append(self.label_values.pop(row))

        nodeToDelete = slicer.util.getNode(segment_name)
        slicer.mrmlScene.RemoveNode(nodeToDelete)

        if self.opaque == segment_name:
            self.opaque = None
        else:
            print('\n\n\n\n\n in delete function', self.opaque, segment_name)

        slicer.util.updateVolumeFromArray(self.predict_node, self.predict_node_array)
        self.createDynamicGrid(self.label_values)

    
    def onSaveButtonClicked(self):
        print(f"Save button clicked")
        with open(str(saved_dir)+self.predict_node.GetName()+'.npy','wb') as f:
            np.save(f,self.predict_node_array)
        with open(str(saved_dir)+self.predict_node.GetName()+'_og.npy','wb') as f:
            np.save(f,self.predict_node_og_array)
        # absolute_difference = np.abs(self.predict_node_array - self.predict_node_og_array)
        # with open(str(saved_dir)+self.predict_node.GetName()+'_abs.npy','wb') as f:
        #     np.save(f,self.absolute_difference)

        sitk_image_predict_node_array = sitk.GetImageFromArray(self.predict_node_array)
        sitk_image_predict_node_array.SetOrigin(self.image_origin)
        sitk_image_predict_node_array.SetSpacing(self.image_spacing)
        sitk_image_predict_node_array.SetDirection(self.image_direction)
        sitk.WriteImage(sitk_image_predict_node_array,str(saved_dir)+self.predict_node.GetName()+'.nii.gz')

        sitk_image_predict_node_og_array = sitk.GetImageFromArray(self.predict_node_og_array)
        sitk_image_predict_node_og_array.SetOrigin(self.image_origin)
        sitk_image_predict_node_og_array.SetSpacing(self.image_spacing)
        sitk_image_predict_node_og_array.SetDirection(self.image_direction)
        sitk.WriteImage(sitk_image_predict_node_og_array,str(saved_dir)+self.predict_node.GetName()+'_og.nii.gz')

    # def onGenerateMapButtonClicked(self):
    #     x = Path(__file__).resolve().parent
    #     print('os.getcwd()',x, Path(x).parent)
    #     raise Exception("This is a custom error message.")


    def onGenerateMapButtonClicked(self):
        print("Generate Uncertainty Map button clicked")
        try:
            self.uncertainty_float_node = slicer.util.getNode('*uncertainty_file*')
            self.predict_node = slicer.util.getNode('*segmentation_file*')
        except Exception as e:
            raise Exception("ERROR: uncertainty file and segmentation file not found. Exception: {}".format(str(e)))

        uncertainty_float_node_array = slicer.util.arrayFromVolume(self.uncertainty_float_node)

        predict_array = slicer.util.arrayFromVolume(self.predict_node)
        self.predict_node_array = np.copy(predict_array)
        self.predict_node_og_array = np.copy(predict_array)


        uncertainty_storage_node = self.uncertainty_float_node.GetStorageNode()
        if uncertainty_storage_node:
            uncertainty_file_path = uncertainty_storage_node.GetFileName()
            sitkimage = sitk.ReadImage(uncertainty_file_path)
        else:
            raise Exception("ERROR: uncertainty file storage node not found.")


        self.image_origin = sitkimage.GetOrigin()
        self.image_spacing = sitkimage.GetSpacing()
        self.image_direction = sitkimage.GetDirection()

        labels_out, N = cc3d.connected_components(uncertainty_float_node_array, return_N=True)
        stats = cc3d.statistics(labels_out)
        # print(stats.keys())
        # print(len(stats['bounding_boxes']))
        # print(stats['bounding_boxes'][0])
        voxel_counts = stats['voxel_counts']
        bounding_boxes = stats['bounding_boxes']
        centroids = stats['centroids']
        uncertainties = []
        # with open(str(saved_dir) + 'labels_out.npy','wb') as f:
        #     np.save(f,labels_out)
        # print("print",len(voxel_counts),N,len(bounding_boxes),len(centroids))


        for i in range(1, N+1):
            value = uncertainty_float_node_array[labels_out == i][0]
            uncertainties.append((i, str(value), voxel_counts[i], bounding_boxes[i], "My_Segment_"+str(i)))

            # if i==50:
            #     break
        # uncertainties.sort(key = lambda x: x[2], reverse = True)
        uncertainties.sort(key = lambda x: float(x[1]), reverse = True)

        self.connected_components = labels_out
        self.total_components = N
        self.label_values = uncertainties        
        self.display_label_values = self.label_values
        # self.createDynamicGrid(self.label_values)




        # labelMapNode = self.createLabelMapVolumeNode()
        # # print("labelMapNode",labelMapNode)
        # print("labelMapNode",labelMapNode.GetStorageNode())
        # # Create a new segmentation node
        # segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        # segmentationNode.CreateDefaultDisplayNodes()  # for display

        # for label in range(1, N+1):
        #     binaryLabelMap = np.zeros(self.connected_components.shape, dtype=np.uint8)
        #     binaryLabelMap[self.connected_components == label] = 1

        #     # Convert the numpy array to a SimpleITK image
        #     binaryLabelMapSitk = sitk.GetImageFromArray(binaryLabelMap)
        #     binaryLabelMapSitk.CopyInformation(sitk.ReadImage(labelMapNode.GetStorageNode().GetFileName()))

        #     # Add the binary label map as a new segment
        #     addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment(f"My_Segment_{label}")
        #     slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(binaryLabelMapSitk, segmentationNode, addedSegmentID)

        # Display the segmentation node
        # slicer.util.setSliceViewerLayers(segmentation=segmentationNode)


        # labelMapVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
        # slicer.util.updateVolumeFromArray(labelMapVolumeNode, self.connected_components)


        
        # for label in range(1,N+1):
        #     component_mask = (labels_out == label).astype(np.uint8)
        #     break

        num_colors = N
        values = np.linspace(0, 1, num_colors)
        self.colors = plt.cm.coolwarm(values)
        self.colors = self.colors[:,:3]
        self.colors = self.colors[::-1, :]

        # print("\n\n\n\n\n\n",len(colors),len(uncertainties))

        for i,uncertainty in enumerate(uncertainties):
            # print(i)
            labelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
            labelmapNode.SetName("MyUncertaintyComponents_"+str(uncertainty[0]))

            # simpleitk - lps
            # slicer - ras
            # https://discourse.slicer.org/t/converting-fiducial-coordinates-from-ras-to-lps/9707

            # # labelmapNode.SetOrigin((0.0, 0.0, 0.0))
            # # labelmapNode.SetOrigin((-214.587890625, -366.587890625, -135.5)) got from simpleitk
            # # LPS<->RAS conversion is just inverting the sign of the first two coordinates
            # labelmapNode.SetOrigin((214.587890625, 366.587890625, -135.5))
            # labelmapNode.SetSpacing((0.82421875, 0.82421875, 1.0))
            # # imageDirections = [[1,0,0], [0,-1,0], [0,0,-1]]
            # # imageDirections = [[1,0,0], [0,1,0], [0,0,1]]  got from simpleitk
            # imageDirections = [[-1,0,0], [0,-1,0], [0,0,1]]
            # labelmapNode.SetIJKToRASDirections(imageDirections)


            labelmapNode.SetOrigin((-self.image_origin[0], -self.image_origin[1], self.image_origin[2]))
            labelmapNode.SetSpacing(self.image_spacing)
            dir_x = list(map(lambda a: a*-1 if a != 0.0 else a, list(self.image_direction[:3]))) 
            dir_y = list(map(lambda a: a*-1 if a != 0.0 else a, list(self.image_direction[3:6]))) 
            dir_z = list(self.image_direction[6:9])
            imageDirections = [dir_x, dir_y, dir_z]
            labelmapNode.SetIJKToRASDirections(imageDirections)

            component_mask = (labels_out == uncertainty[0]).astype(np.uint8)

            slicer.util.updateVolumeFromArray(labelmapNode, component_mask)

            seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
            seg.SetName(uncertainty[4])
            slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapNode, seg)
            seg.CreateClosedSurfaceRepresentation()
            slicer.mrmlScene.RemoveNode(labelmapNode)
            segmentation = seg.GetSegmentation()
            segment = segmentation.GetSegment(segmentation.GetNthSegmentID(0))
            # segment.SetColor(self.colors[i])
            # segment.SetColor(self.colors[uncertainty[0]-1])
            segment.SetColor(self.colors[i])

            seg.GetDisplayNode().SetOpacity(0.2)
            # seg.GetDisplayNode().SetOpacity(1)

            # if i==50:
            #     break

        self.createDynamicGrid(self.display_label_values)




    def onDynamicButtonClicked(self, value):
        print(f"Button clicked for label: {value}")


    def onApplyButton(self) -> None:
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            self.logic.process(
                self.ui.inputSelector.currentNode(),
                self.ui.outputSelector.currentNode(),
                self.ui.imageThresholdSliderWidget.value,
                self.ui.invertOutputCheckBox.checked
            )

            if self.ui.invertedOutputSelector.currentNode():
                self.logic.process(
                    self.ui.inputSelector.currentNode(),
                    self.ui.invertedOutputSelector.currentNode(),
                    self.ui.imageThresholdSliderWidget.value,
                    not self.ui.invertOutputCheckBox.checked,
                    showResult=False
                )



    def cleanup(self) -> None:
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self) -> None:
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[NewParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume and self._parameterNode.thresholdedVolume:
            self.ui.applyButton.toolTip = "Compute output volume"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input and output volume nodes"
            self.ui.applyButton.enabled = False

    def onApplyButton(self) -> None:
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
                               self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)

            # Compute inverted output (if needed)
            if self.ui.invertedOutputSelector.currentNode():
                # If additional output volume is selected then result with inverted threshold is written there
                self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
                                   self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)


#
# NewLogic
#

class NewLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return NewParameterNode(super().getParameterNode())

    def process(self,
                inputVolume: vtkMRMLScalarVolumeNode,
                outputVolume: vtkMRMLScalarVolumeNode,
                imageThreshold: float,
                invert: bool = False,
                showResult: bool = True) -> None:
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': imageThreshold,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# NewTest
#

class NewTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_New1()

    def test_New1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('New1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = NewLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')








# for component_label in range(1, N + 1):

#     labelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
#     labelmapNode.SetName("MyUncertaintyComponents"+str(component_label))

#     labelmapNode.SetOrigin((0.0, 0.0, 0.0))
#     labelmapNode.SetSpacing((0.82421875, 0.82421875, 1.0))
#     imageDirections = [[1,0,0], [0,-1,0], [0,0,-1]]
#     labelmapNode.SetIJKToRASDirections(imageDirections)

#     component_mask = (labels_out == component_label).astype(np.uint8)

#     slicer.util.updateVolumeFromArray(labelmapNode, component_mask)

#     seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
#     slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapNode, seg)
#     seg.CreateClosedSurfaceRepresentation()
#     slicer.mrmlScene.RemoveNode(labelmapNode)



# https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#get-centroid-of-each-segment
# https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#get-centroid-of-a-segment-in-world-ras-coordinates
# https://slicer.readthedocs.io/en/latest/developer_guide/script_repository/segmentations.html#get-centroid-of-a-segment-in-world-ras-coordinates