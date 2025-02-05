import bpy

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
