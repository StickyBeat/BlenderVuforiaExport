BlenderVuforiaExport
====================

This is an export script for Blender which matches the format used in the iOS examples provided with the Vuforia SDK, which is a popular augmented reality framework.

http://www.blender.org

https://vuforia.com

Credits
-------

The export script was largely based on the excellent work of Krzysztof Soï¿½ek (not sure about the spelling here). His exporter script extracts and exports all the neccessary data, I pretty much just adjusted the output format and added another export option. Here's where I found his work:

http://ksolek.fm.interia.pl/Blender/

What it's for
-------------

So let's say you install Vuforia iOS SDK, you start looking at the basic examples, you pick ImageTargets, you start poking around in the code, and you find this bit:

    obj3D.numVertices = NUM_TEAPOT_OBJECT_VERTEX;
    obj3D.vertices = teapotVertices;
    obj3D.normals = teapotNormals;
    obj3D.texCoords = teapotTexCoords;
    obj3D.numIndices = NUM_TEAPOT_OBJECT_INDEX;
    obj3D.indices = teapotIndices;

That seems to be where the 3D model data is passed to the engine. The data itself is in a separate file called Teapot.h, which is included by a simple include directive:

	#import "Teapot.h"

What you want is to generate your own file like that, and modify the code so that it loads your data instead. This is what this exporter is for. 

Let's say you have a Blender file with a 3D model of a cat. The name of the object is "cat". You run the export (see installation and usage further down). It will produce a file which you save as cat.h. You add this file to the XCode project, add another #include at the top of the code, and modify the code like so:

    obj3D.numVertices = NUM_CAT_OBJECT_VERTEX;
    obj3D.vertices = catVertices;
    obj3D.normals = catNormals;
    obj3D.texCoords = catTexCoords;
    obj3D.numIndices = NUM_CAT_OBJECT_INDEX;
    obj3D.indices = catIndices;

That's pretty much it as far as the model is concerned. However, I got tired of changing around six names like that, so I had the exporter create a struct and make an instance of that struct, holding the fields needed. This will let you do this instead:

    BlenderExportedObject object = catObject;
    
    obj3D.numVertices = object.numVertices;
    obj3D.vertices = object.vertices;
    obj3D.normals = object.normals;
    obj3D.texCoords = object.texCoords;
    obj3D.numIndices = object.numIndices;
    obj3D.indices = object.indices;

The result will be exactly the same, only when you want to change it to a dinosaur instead of a cat, you'll only need to change catObject to dinosaurObject. You get it.

The texture, of course, is another matter. I won't go into it in detail here, but it's not difficult. You only need to include the cat texture in the project, find the part where the example teapot texture is loaded, and replace the filename.

Installation and usage
----------------------

Krzysztof provides great info and screenshots of installation and usage on his page. I'll only give a brief text version here. 

1. Copy the folder "io_mesh_ogl_vuforia" into Blenders addons folder, on a Mac the path will be something like Applications/blender.app/Contents/MacOS/2.xx/scripts
2. In Blender, go File -> User Preferences -> Addons -> Import-Export -> Import-Export: Vuforia OpenGL export / C -> *Check*
3. To use it, go File -> Export -> Vuforia OpenGL C include (.h)

Options
-------

In the Save dialog, there are export options on the left side. Krzysztof included a checkbox to include all objects in scene or just the selected object. That's useful, so I left it intact. I added another option, which will scale the model so that the widest part of the object in any axis would match the value provided. Set it to zero if you don't want to use this feature.

Good to know
------------

I have experienced models where the exporter has output blank texture coordinates (all zeros). If this happens to you, the fix may be as easy as checking the "Object Data > UV Maps" option in Blender. Thanks to Mariano Patafio for bringing this up so I can add this info.

Comments and suggestions
------------------------

Mail that stuff to erik@stickybeat.se. 

Hope you put the exporter to good use, now.

