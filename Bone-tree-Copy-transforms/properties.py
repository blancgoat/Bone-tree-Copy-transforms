import bpy
from .utils import validate_armature

class CopyTransformsProperties(bpy.types.PropertyGroup):
    parent_armature: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Parent Armature",
        description="Armature containing the root bone",
        update=lambda self, context: validate_armature(self.parent_armature, context, "parent_armature")
    )
    child_armature: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Child Armature",
        description="Target child armature to apply constraints to",
        update=lambda self, context: validate_armature(self.child_armature, context, "child_armature")
    )
    root_bone: bpy.props.StringProperty(
        name="Root Bone",
        description="Root bone to start traversal from"
    )
    traverse_mode: bpy.props.EnumProperty(
        name="Traversal Mode",
        description="Choose how to traverse the bones",
        items=[
            ('PARENT_BASED', "Parent-Based", "Traverse starting from root bone to its children"),
            ('CHILD_BASED', "Child-Based", "Traverse child armature bones starting from root bone")
        ],
        default='PARENT_BASED'
    )
