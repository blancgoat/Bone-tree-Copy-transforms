bl_info = {
    "name": "Bone tree Copy Transforms",
    "author": "blancgoat",
    "version": (0, 3, 7),
    "blender": (4, 2, 4),
    "location": "View3D > Sidebar > Bonetree",
    "description": "",
    "warning": "",
    "wiki_url": "https://github.com/blancgoat/Bone-tree-Copy-transforms",
    "category": "Rigging",
}

import bpy

# ----------------- Helper Function -----------------
def validate_armature(obj, context, prop_name):
    """Validate if the selected object is an Armature, otherwise clear it."""
    if obj and obj.type != 'ARMATURE':
        def draw(self, context):
            self.layout.label(text=f"'{obj.name}' is not an Armature object!")
        bpy.context.window_manager.popup_menu(draw, title="Invalid Selection", icon='ERROR')
        setattr(context.scene.copy_transforms_props, prop_name, None)

# ----------------- Property Group -----------------
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

# ----------------- Operator -----------------
class OBJECT_OT_copy_transforms_operator(bpy.types.Operator):
    """Add Copy Transforms constraints from root bone to child armature"""
    bl_idname = "object.copy_transforms_single_child"
    bl_label = "Apply Copy Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.copy_transforms_props
        
        # Validate selections
        if not props.parent_armature or props.parent_armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No valid parent armature selected.")
            return {'CANCELLED'}

        if not props.child_armature or props.child_armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No valid child armature selected.")
            return {'CANCELLED'}

        if not props.root_bone:
            self.report({'ERROR'}, "No root bone selected.")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        parent_armature = props.parent_armature
        child_armature = props.child_armature

        root_bone = parent_armature.pose.bones.get(props.root_bone)
        if not root_bone:
            self.report({'ERROR'}, f"Root bone '{props.root_bone}' not found in parent armature.")
            return {'CANCELLED'}
        
        bone_count = 0

        def add_constraints_recursive(bone):
            nonlocal bone_count
            if props.traverse_mode == 'PARENT_BASED':
                if bone.name in child_armature.pose.bones:
                    constraint = child_armature.pose.bones[bone.name].constraints.new(type='COPY_TRANSFORMS')
                    constraint.target = parent_armature
                    constraint.subtarget = bone.name
                    bone_count += 1
                for child_bone in bone.children:
                    add_constraints_recursive(child_bone)
            elif props.traverse_mode == 'CHILD_BASED':
                for bone in child_armature.pose.bones:
                    if bone.name in parent_armature.pose.bones:
                        constraint = bone.constraints.new(type='COPY_TRANSFORMS')
                        constraint.target = parent_armature
                        constraint.subtarget = bone.name
                        bone_count += 1

        add_constraints_recursive(root_bone)
        self.report({'INFO'}, f"Total bones with constraints: {bone_count}")
        return {'FINISHED'}
    
# ----------------- Remove Operator -----------------    
class OBJECT_OT_remove_copy_transforms_operator(bpy.types.Operator):
    """Remove all Copy Transforms constraints from the child armature"""
    bl_idname = "object.remove_copy_transforms"
    bl_label = "Remove Copy Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.copy_transforms_props

        # Validate selections
        if not props.child_armature or props.child_armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No valid child armature selected.")
            return {'CANCELLED'}

        child_armature = props.child_armature

        # Remove COPY_TRANSFORMS constraints
        removed_count = 0
        for bone in child_armature.pose.bones:
            constraints = bone.constraints
            for constraint in constraints:
                if constraint.type == 'COPY_TRANSFORMS':
                    constraints.remove(constraint)
                    removed_count += 1

        # Alert the user
        self.report({'INFO'}, f"Removed {removed_count} Copy Transforms constraints.")
        return {'FINISHED'}

# ----------------- UI Panel -----------------
class VIEW3D_PT_copy_transforms_panel(bpy.types.Panel):
    """Creates a Panel in the 3D View sidebar"""
    bl_label = "Bone tree Copy Transforms"
    bl_idname = "VIEW3D_PT_copy_transforms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bonetree'

    def draw(self, context):
        layout = self.layout
        props = context.scene.copy_transforms_props

        # Parent Armature
        box = layout.box()
        row = box.row()
        row.label(text="Parent Armature:")
        row.prop(props, "parent_armature", text="")

        # Child Armature
        box = layout.box()
        row = box.row()
        row.label(text="Child Armature:")
        row.prop(props, "child_armature", text="")

        # Root Bone Selection (Child bones only)
        if props.parent_armature and props.child_armature:
            box = layout.box()
            row = box.row()
            row.label(text="Root Bone:")
            row.prop_search(props, "root_bone", props.child_armature.pose, "bones", text="")

        # Traverse Mode
        box = layout.box()
        row = box.row()
        row.label(text="Traversal Mode:")
        row.prop(props, "traverse_mode", expand=True)

        # Apply and Remove Buttons
        if props.parent_armature and props.child_armature and props.root_bone:
            layout.operator("object.copy_transforms_single_child", text="Apply Copy Transforms", icon='CHECKMARK')
            layout.operator("object.remove_copy_transforms", text="Remove Copy Transforms", icon='CANCEL')
        else:
            layout.label(text="Complete all selections to apply/remove", icon='ERROR')

# ----------------- Register -----------------
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