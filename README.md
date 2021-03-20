# **WASP Med Blender Add-on (BLENDER ADD-ON)**

![WASP Med Blender Add-on](https://www.3dwasp.com/wp-content/uploads/2019/07/Blenderwasp_big-1-1-1024x536.jpg)  
WASP Med Blender Add-on is developed by WASP MED with **Alessandro Zomparelli** for modeling orthoses starting from 3D scans.  

## **INSTALLATION**

### Note:

**blender version 2.80 is currently the only supported version**

A download is avaible [Here](https://download.blender.org/release/Blender2.80/blender-2.80rc3-windows64.zip) For 64 bit Windows.

* Download “WASP Med” from Github
* Start Blender: open User Preferences>Add-ons
* Click “Install from file” and point Blender at the downloaded .zip
* Activate “WASP Med” add-on from User Preferences
* Save User Preferences if you want to have it on at startup
* Utility

## **DESCRIPTION**

WASP Med Add-on Blender is a tool developed for modeling orthoses starting from 3D scans. The models created are also suitable for 3D printing. The whole modeling process has been studied in a way that guides the user step-by-step until the final product, leaving the freedom to operate laterly with the complete set of Blender tools.  

## **USAGE & TOOLS**

### **Importing the scan**

The add-on makes the importing of the mesh easier, with an automatical preset of the user interface and units of measure. It allows importing both .stl and .obj files. The system also includes a command for centering the object on the scene with the right reference, supporting 4C WASP Bust scanner.  

### **Reconstruction of the topology (remesh)**

With Blender’s powerful remesh modifier it is possible to reconstruct and fix the data from any kind of scan removing errors like holes, double edges, auto-intersecting surfaces and switched normals. In this phase is possible to choose the “resolution” to work with: we consider the useful depth 7 to 9\. A higher resolution gives better results and definition but it’s heavier for the computing. It also makes the file heavier.  

### **Sculpting environment**

In sculpting environment you can use tools for modifying the mesh as if it was clay with operations like smoothing, adding material, inflating, flattening and grabbing the matter.  

### **Deformation with control cage (Lattice)**

By using the control cage is possible to move, translate and twist different areas of the object. This works with Lattice modifier and is useful for creating corrections.  

### **Crop tools**

Move and rotate the pre-built planes and decide what to cut off from your model that you don’t need.  

### **Drawing of the profiles**

In this phase, it is possible to “paint” areas of the object that will be controlled in various ways in the next step.  

### **Definition of measures and borders**

Now you can decide different thicknesses for the two painted parts. One of the two can also be removed (by using value 0mm). You can choose the behavior on the borders with standard profiles or with customized ones. Also you have two tools: one for smoothing the support parts, one for cropping the scraps.  

### **Exporting the mesh**

In this phase the mesh is generated and you have the possibility to export it and have it ready for the 3D printing or making further and different operation in the environment of Blender 2.8.  

### **Utility**

The add-on also features tools for the measuring of the circumference and the visualizing how much the model is modified in each phase.  

## **DEVELOPMENT**

“WASP Med” Blender Add-on is a tool created by WASP and Alessandro Zomparelli in an open-source philosophy. The idea is making easier for everyone to create orthoses with the use of 3D printers.
