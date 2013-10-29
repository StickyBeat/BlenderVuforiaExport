

import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

filename = os.path.join(os.path.dirname( os.path.realpath(__file__) ), "export_ogl_vuforia.py")

exec(compile(open(filename).read(), filename, 'exec'))

export( "test.h", True, 100 )


