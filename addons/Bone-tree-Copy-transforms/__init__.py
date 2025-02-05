bl_info = {
    "name": "Bone tree Copy Transforms",
    "author": "blancgoat",
    "version": (1, 0, 0),
    "blender": (4, 2, 4),
    "location": "View3D > Sidebar > Bonetree",
    "description": "",
    "warning": "",
    "wiki_url": "https://github.com/blancgoat/Bone-tree-Copy-transforms",
    "category": "Rigging",
}

import bpy
from .properties import CopyTransformsProperties
from .operators import OBJECT_OT_copy_transforms_operator, OBJECT_OT_remove_copy_transforms_operator
from .ui import VIEW3D_PT_copy_transforms_panel

classes = [
    CopyTransformsProperties,
    OBJECT_OT_copy_transforms_operator,
    OBJECT_OT_remove_copy_transforms_operator,
    VIEW3D_PT_copy_transforms_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.copy_transforms_props = bpy.props.PointerProperty(type=CopyTransformsProperties)

def unregister():
    del bpy.types.Scene.copy_transforms_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()