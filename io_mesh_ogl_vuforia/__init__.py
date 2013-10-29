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


bl_info = {
    "name": "Vuforia OpenGL export / C",
    "author": "Krzysztof Solek / Erik Gustavsson",
    "blender": (2, 5, 7),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Export mesh data with UV's into Vuforia friendly C/OpenGL format",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    if "export_ogl_vuforia" in locals():
        imp.reload(export_ogl_vuforia)

import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty, FloatProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ExportOGL(bpy.types.Operator, ExportHelper):
    '''Export a whole scene or single object as an OpenGL / C include file with normals and texture coordinates'''
    bl_idname = "export_ogl_vuforia.ply"
    bl_label = "Export OpenGL for Vuforia"

    filename_ext = ".h"
    filter_glob = StringProperty(default="*.h", options={'HIDDEN'})

    entire_scene = BoolProperty(name="Entire Scene", description="Export all MESH object (Entire scene)", default=True)
    scale_to = FloatProperty(name="Scale Objects To", description="Scale objects to given size", default=128)

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        from . import export_ogl_vuforia
        return export_ogl_vuforia.export(filepath, self.entire_scene, self.scale_to)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "entire_scene")

        row = layout.row()
        row.prop(self, "scale_to")

def menu_func_export(self, context):
    self.layout.operator(ExportOGL.bl_idname, text="Vuforia OpenGL C Include (.h)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
