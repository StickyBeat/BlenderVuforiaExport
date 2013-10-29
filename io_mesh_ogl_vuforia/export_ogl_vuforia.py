# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#############################################################
#	(C) Krzysztof Solek, Mielec 2012
#############################################################

import bpy

import os

###########################################################
#
#       Global variables
#
###########################################################
obj_names=[]    # names of meshes in "C-suitable" format
vtx = []      # list of dictionaries for each mesh
faces = []    # list of lists
vl = []       # list of vertices for each mesh
nl = []       # list of normals for each mesh
uvl =   []    # list of UV coords for each mesh
obj_mtx=[]  # list of local transformations for each object
obj_cnt =   0   # object count
max_vcnt=   0   # qty of vertices for biggest mesh

###########################################################
#
#   Round values of the 3D vector
#
###########################################################

def r3d(v):
    return round(v[0],6), round(v[1],6), round(v[2],6)

###########################################################
#
#   Round values of the 2D vector
#
###########################################################

def r2d(v):
    return round(v[0],6), round(v[1],6)


###########################################################
#
#   Convert object name to be suitable for C definition
#
###########################################################

def clearName(name):
    tmp=name; #.upper()
    ret=""
    for i in tmp:
        if (i in " ./\-+#$%^!@"):
            ret=ret+"_"
        else:
            ret=ret+i
    return ret


###########################################################
#
#   Build data for each object (MESH)
#
###########################################################

def buildData (obj, msh, name):
    global obj_cnt
    global obj_names     # names of meshes in "C-suitable" format
    global vtx           # list of dictionaries for each mesh
    global faces         # list of lists
    global vl            # list of vertices for each mesh
    global nl            # list of normals for each mesh
    global uvl          # list of UV coords for each mesh
    global obj_mtx      # list of local transformations for each object

    lvdic = {} # local dictionary
    lfl = [] # lcoal faces index list
    lvl = [] # local vertex list
    lnl = [] # local normal list
    luvl = [] # local uv list
    lvcnt = 0 # local vertices count
    isSmooth = False
    hasUV = True    # true by default, it will be verified below
    
    print("Building for: %s\n"%obj.name)

    if (len(msh.tessface_uv_textures)>0):
        if (msh.tessface_uv_textures.active is None):
            hasUV=False
    else:
        hasUV = False
     
    if (hasUV):
        activeUV = msh.tessface_uv_textures.active.data
        
    obj_names.append(clearName(name))
    obj_cnt+=1
    
    for i,f in enumerate(msh.tessfaces):
        isSmooth = f.use_smooth
        tmpfaces = []
        for j,v in enumerate(f.vertices):  
            vec = msh.vertices[v].co
            vec = r3d(vec)
            
            if (isSmooth):  # use vertex normal
                nor = msh.vertices[v].normal
            else:           # use face normal
                nor = f.normal
            
            nor = r3d(nor)
            
            if (hasUV):
                co = activeUV[i].uv[j]
                co = r2d(co)
            else:
                co = (0.0, 0.0)
            
            key = vec, nor, co
            vinx = lvdic.get(key)
            
            if (vinx is None): # vertex not found
                lvdic[key] = lvcnt
                lvl.append(vec)
                lnl.append(nor)
                luvl.append(co)
                tmpfaces.append(lvcnt)
                lvcnt+=1
            else:
                inx = lvdic[key]
                tmpfaces.append(inx)
        
        if (len(tmpfaces)==3): 
            lfl.append(tmpfaces)
        else:
            lfl.append([tmpfaces[0], tmpfaces[1], tmpfaces[2]])
            lfl.append([tmpfaces[0], tmpfaces[2], tmpfaces[3]])

    
    #update global lists and dictionaries
    vtx.append(lvdic)        
    faces.append(lfl)
    vl.append(lvl)
    nl.append(lnl)
    uvl.append(luvl)
    obj_mtx.append(obj.matrix_local)



###########################################################
#
#       Save data to C header file
#
###########################################################
    
def save(filename,scale_to=0):

    defName = "_" + clearName( filename ).upper() + "_BLENDER_EXPORT_H_"

    file = open(filename, "w", newline="\n")
    file.write("#ifndef %s\n" % defName )
    file.write("#define %s\n" % defName )
    file.write("\n")


    structDefinition = """

#ifndef _BLENDER_EXPORT_OBJECT_STRUCT_
#define _BLENDER_EXPORT_OBJECT_STRUCT_

struct BlenderExportedObject{
    
    unsigned int numVertices;
    const float *vertices;
    const float *normals;
    const float *texCoords;
    
    unsigned int numIndices;
    const unsigned short *indices;

    const float *transform;
    
};

#endif

"""

    file.write( structDefinition )

    file.write("#define NUM_OBJECTS %d\n"%obj_cnt)

    for index,name in enumerate(obj_names):

        camelName = name[0].lower() + name[1:];
        upperName = name.upper();

        v = vl[ index ]
        f = faces[ index ];
        uv = uvl[ index ];
        n = nl[ index ];
        o = obj_mtx[ index ];

        numberOfVerticesConstantName = "NUM_" + upperName + "_OBJECT_VERTEX";

        file.write( "#define " )
        file.write( numberOfVerticesConstantName )
        file.write( " " )
        file.write ("%d"%len(v))
        file.write( "\n" )



        numberOfIndicesConstantName = "NUM_" + upperName + "_OBJECT_INDEX";

        file.write( "#define " )
        file.write( numberOfIndicesConstantName )
        file.write( " " )
        file.write ("%d"%len(f))
        file.write( " * 3\n" )

        file.write( "\n" )



        spans = [ (0,0), (0,0), (0,0) ];

        for j in range(0,len(v)):

            vv = v[j]

            for axisIndex in range( 0, len( vv ) ):

                point = vv[ axisIndex ]

                if( j == 0 ):
                    
                    spans[ axisIndex ] = ( point, point )

                else:

                    ( min, max ) = spans[ axisIndex ]

                    if( point < min ):
                        min = point

                    if( point > max ):
                        max = point

                    spans[ axisIndex ] = ( min, max )

        maxDiff = 0

        for axisIndex in range( 0, len( spans ) ):

            ( min, max ) = spans[ axisIndex ]

            diff = max - min

            if diff > maxDiff:
                maxDiff = diff

        if scale_to != 0:

            targetSize = scale_to

            scale = targetSize / maxDiff

            print( "scale: %f -> %f" % (scale,scale_to) )

        else:
            scale = 1


        verticesConstantName = camelName + "Vertices"

        file.write( "static const float " + verticesConstantName + "[ " + numberOfVerticesConstantName + " * 3 ] = {\n\t" )

        for j in range(0,len(v)):

            vv = v[j]

            for axisIndex in range( 0, len( vv ) ):

                point = vv[ axisIndex ]
                ( min, max ) = spans[ axisIndex ]

                #point -= min
                point *= scale

                file.write ("%ff, "%point)

        file.write( "\n};\n" )
        file.write( "\n" )


        textureCoordinatesConstantName = camelName + "TexCoords"

        file.write( "static const float " + textureCoordinatesConstantName + "[ " + numberOfVerticesConstantName + " * 2 ] = {\n\t" )

        for j in range(0,len(uv)):

            file.write ("%ff, %ff, "%tuple(uv[j]))

        file.write( "\n};\n" )
        file.write( "\n" )


        normalsConstantName = camelName + "Normals"

        file.write( "static const float " + normalsConstantName + "[ " + numberOfVerticesConstantName + " * 3 ] = {\n\t" )

        for j in range(0,len(n)):

            file.write ("%ff, %ff, %ff, "%tuple(n[j]))

        file.write( "\n};\n" )
        file.write( "\n" )        


        indicesConstantName = camelName + "Indices"

        file.write( "static const unsigned short " + indicesConstantName + "[ " + numberOfIndicesConstantName + " ] = {\n\t" )

        for j in range(0,len(f)):

            file.write ("%d, %d, %d, "%tuple(f[j])) 

        file.write( "\n};\n" )
        file.write( "\n" )        


        transformConstantName = camelName + "Transform"

        file.write( "static const float " + transformConstantName + "[ 16 ] = {\n" )

        file.write("\t%ff, %ff, %ff, %ff,\n"%tuple(o.col[0]))
        file.write("\t%ff, %ff, %ff, %ff,\n"%tuple(o.col[1]))
        file.write("\t%ff, %ff, %ff, %ff,\n"%tuple(o.col[2]))
        file.write("\t%ff, %ff, %ff, %ff,\n"%tuple(o.col[3]))

        file.write( "\n};\n" )
        file.write( "\n" )




        file.write( "static const BlenderExportedObject %sObject = {\n" % camelName )

        file.write( "\t%s,\n" % numberOfVerticesConstantName )
        file.write( "\t%s,\n" % verticesConstantName )
        file.write( "\t%s,\n" % normalsConstantName )
        file.write( "\t%s,\n" % textureCoordinatesConstantName )
        file.write( "\t%s,\n" % numberOfIndicesConstantName )
        file.write( "\t%s,\n" % indicesConstantName )
        file.write( "\t%s,\n" % transformConstantName )

        file.write( "};\n" );
        file.write( "\n" );
        
    file.write ("#endif")   
    file.close()
###########################################################
#
#       Export MESH object. By default export whole scene
#
###########################################################

def export(filename="untitled.h", entire_scene=True, scale_to=0 ):
    global obj_cnt
    global obj_names     # names of meshes in "C-suitable" format
    global vtx           # list of dictionaries for each mesh
    global faces         # list of lists
    global vl            # list of vertices for each mesh
    global nl            # list of normals for each mesh
    global uvl          # list of UV coords for each mesh
    global obj_mtx      # list of local transformations for each object

    print("--------------------------------------------------\n")
    print("Starting script:\n")
    print(filename)

    # clear all gloabl variables
    obj_names=[]    # names of meshes in "C-suitable" format
    vtx = []      # list of dictionaries for each mesh
    faces = []    # list of lists
    vl = []       # list of vertices for each mesh
    nl = []       # list of normals for each mesh
    uvl =   []    # list of UV coords for each mesh
    obj_mtx=[]  # list of local transformations for each object
    obj_cnt =   0   # object count
    max_vcnt=   0   # qty of vertices for biggest mesh


    sc = bpy.context.scene  # export MESHes from active scene

    if (entire_scene):
        for o in sc.objects:

            if (o.type=="MESH" or o.type=="CURVE"):    # export ONLY meshes. and curves, too?
                msh = o.to_mesh(sc,True,"PREVIEW") # prepare MESH
                buildData(o, msh, o.name)
                bpy.data.meshes.remove(msh)
    else:
        o = sc.objects.active
        msh = o.to_mesh(sc,True,'PREVIEW')
        buildData(o, msh, o.name)
        bpy.data.meshes.remove(msh)

    save(filename,scale_to)    

    print("Done\n")
    return {'FINISHED'}


