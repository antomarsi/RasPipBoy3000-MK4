# About this code

This is a quick hack that loads a OBJ file and allows you to convert OBJ objects to spinning animations for the Pip-Boy

# OBJFileLoader

Edited from: https://www.pygame.org/wiki/OBJFileLoader

# Viewer

To view an OBJ-file run:

    python OBJFileLoader/objviewer.py .\folderwithobjfile\
	
	If the textures are reversed press the up arrow before exporting
	Press left to export a clockwise animation
	Press right to export a counterclockwise animation
	
	To map textues map_Kd image.png must be in the MTL file on each node, otherwise it will render as white.
	
	Adjust the angle variable in the code to change the number of faces.
	Adjust the swapyz variable if the object load sideways
	
	I post process the images to brighten them up a bit before use
