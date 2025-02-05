import bpy

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