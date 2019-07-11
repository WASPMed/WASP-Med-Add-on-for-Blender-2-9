<h1><strong>WASP Med Blender Add-on (BLENDER ADD-ON)</h1></strong>
<br>
<img src="https://www.3dwasp.com/wp-content/uploads/2019/07/Blenderwasp_big-1-1-1024x536.jpg" alt="WASP Med Blender Add-on">
<br>
WASP Med Blender Add-on is developed by WASP MED with <strong>Alessandro Zomparelli</strong> for modeling orthoses starting from 3D scans.
<br>
<h2><strong>INSTALLATION</h2></strong>
<ul>
<li>Download “WASP Med” from Github</li>
<li>Start Blender: open User Preferences>Add-ons</li>
<li>Click “Install from file” and point Blender at the downloaded .zip</li>
<li>Activate “WASP Med” add-on from User Preferences</li>
<li>Save User Preferences if you want to have it on at startup</li>
<li>Utility</li>
</ul>
<br>
<h2><strong>DESCRIPTION</h2></strong>
<br>
WASP Med Add-on Blender is a tool developed for modeling orthoses starting from 3D scans. The models created are also suitable for 3D printing.
The whole modeling process has been studied in a way that guides the user step-by-step until the final product, leaving the freedom to operate laterly with the complete set of Blender tools.
<br>
<br>
<h2><strong>USAGE & TOOLS</h2></strong>
<br>
<h3><strong>Importing the scan</h3></strong>
The add-on makes the importing of the mesh easier, with an automatical preset of the user interface and units of measure.
It allows importing both .stl and .obj files.
The system also includes a command for centering the object on the scene with the right reference, supporting 4C WASP Bust scanner.
<br>
<h3><strong>Reconstruction of the topology (remesh)</h3></strong>
With Blender’s powerful remesh modifier it is possible to reconstruct and fix the data from any kind of scan removing errors like holes, double edges, auto-intersecting surfaces and switched normals.
In this phase is possible to choose the “resolution” to work with: we consider the useful depth 7 to 9. A higher resolution gives better results and definition but it’s heavier for the computing. It also makes the file heavier.
<br>
<h3><strong>Sculpting environment</h3></strong>
In sculpting environment you can use tools for modifying the mesh as if it was clay with operations like smoothing, adding material, inflating, flattening and grabbing the matter.
<br>
<h3><strong>Deformation with control cage (Lattice)</h3></strong>
By using the control cage is possible to move, translate and twist different areas of the object. This works with Lattice modifier and is useful for creating corrections.
<br>
<h3><strong>Crop tools</h3></strong>
Move and rotate the pre-built planes and decide what to cut off from your model that you don’t need.
<br>
<h3><strong>Drawing of the profiles</h3></strong>
In this phase, it is possible to “paint” areas of the object that will be controlled in various ways in the next step.
<br>
<h3><strong>Definition of measures and borders</h3></strong>
Now you can decide different thicknesses for the two painted parts. One of the two can also be removed (by using value 0mm).
You can choose the behavior on the borders with standard profiles or with customized ones.
Also you have two tools: one for smoothing the support parts, one for cropping the scraps.
<br>
<h3><strong>Exporting the mesh</h3></strong>
In this phase the mesh is generated and you have the possibility to export it and have it ready for the 3D printing or making further and different operation in the environment of Blender 2.8.
<br>
<h3><strong>Utility</h3></strong>
The add-on also features tools for the measuring of the circumference and the visualizing how much the model is modified in each phase.
<br>
<h2><strong>DEVELOPMENT</h2></strong>
<br>
“WASP Med” Blender Add-on is a tool created by WASP and Alessandro Zomparelli in an open-source philosophy. The idea is making easier for everyone to create orthoses with the use of 3D printers.
