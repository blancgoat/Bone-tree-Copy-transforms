bl_info = {
    "name": "Bone tree Copy Transforms",
    "author": "blancgoat",
    "version": (0, 3, 2),
    "blender": (4, 2, 4),
    "location": "View3D > Sidebar > Bonetree",
    "description": "",
    "warning": "",
    "wiki_url": "https://github.com/blancgoat",
    "category": "Rigging",
}

import bpy

# ----------------- Property Group -----------------
class CopyTransformsProperties(bpy.types.PropertyGroup):
    """Property group to store selected armatures and bone information"""
    parent_armature: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Parent Armature",
        description="Armature containing the root bone"
    )
    
    child_armature_names: bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup,
        name="Child Armature Names",
        description="Names of child armatures to apply copy transforms to"
    )
    
    root_bone: bpy.props.StringProperty(
        name="Root Bone",
        description="Root bone to start traversal from"
    )

    traverse_mode: bpy.props.EnumProperty(
        name="Traversal Mode",
        description="Choose how to traverse the bones",
        items=[
            ('PARENT_BASED', "Root Bone (Parent-Based)", "Traverse starting from root bone and its children"),
            ('CHILD_BASED', "Root Bone (Child-Based)", "Traverse all child bones starting from root bone")
        ],
        default='PARENT_BASED'
    )

# ----------------- Operator -----------------
class OBJECT_OT_copy_transforms_operator(bpy.types.Operator):
    """Add Copy Transforms constraints from root bone to child armatures"""
    bl_idname = "object.copy_transforms_multi_armature"
    bl_label = "Apply Copy Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.copy_transforms_props

        # Validate selections
        if not props.parent_armature:
            self.report({'ERROR'}, "No parent armature selected.")
            return {'CANCELLED'}

        if len(props.child_armature_names) == 0:
            self.report({'ERROR'}, "No child armatures selected.")
            return {'CANCELLED'}

        if not props.root_bone:
            self.report({'ERROR'}, "No root bone selected.")
            return {'CANCELLED'}

        # Object Mode 강제 설정
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bone_count_total = 0

        # 부모 Armature와 Root Bone
        parent_armature = props.parent_armature
        root_bone = parent_armature.pose.bones.get(props.root_bone)

        if not root_bone:
            self.report({'ERROR'}, f"Root bone '{props.root_bone}' not found in parent armature.")
            return {'CANCELLED'}

        # Find child armatures by name
        child_armatures = [
            obj for obj in bpy.data.objects
            if obj.type == 'ARMATURE' and obj.name in [item.name for item in props.child_armature_names]
        ]

        # Traverse Mode에 따른 처리
        if props.traverse_mode == 'PARENT_BASED':
            # Root Bone (Parent-Based): Root Bone부터 하위 본 순회
            def add_constraints_parent_based(bone, child_armature):
                nonlocal bone_count_total
                if bone.name in child_armature.pose.bones:
                    constraint = child_armature.pose.bones[bone.name].constraints.new(type='COPY_TRANSFORMS')
                    constraint.target = parent_armature
                    constraint.subtarget = bone.name
                    bone_count_total += 1
                for child_bone in bone.children_recursive:
                    add_constraints_parent_based(child_bone, child_armature)

            for child_armature in child_armatures:
                add_constraints_parent_based(root_bone, child_armature)

        elif props.traverse_mode == 'CHILD_BASED':
            # Root Bone (Child-Based): 모든 본을 자식 Armature 기준으로 순회
            def add_constraints_child_based(child_armature):
                nonlocal bone_count_total
                for bone in child_armature.pose.bones:
                    if bone.name in parent_armature.pose.bones:
                        constraint = bone.constraints.new(type='COPY_TRANSFORMS')
                        constraint.target = parent_armature
                        constraint.subtarget = bone.name
                        bone_count_total += 1

            for child_armature in child_armatures:
                add_constraints_child_based(child_armature)

        self.report({'INFO'}, f"Total constraints added: {bone_count_total}")
        return {'FINISHED'}

# ----------------- Scene Update Handler -----------------
def update_armature_selection(scene):
    """Update parent and child armature selection based on current scene state."""
    props = scene.copy_transforms_props

    # 선택된 모든 객체 중 Armature만 필터링
    selected_objects = [obj for obj in scene.objects if obj.select_get()]
    selected_armatures = [obj for obj in selected_objects if obj.type == 'ARMATURE']

    # 부모 Armature: 활성화된 (마지막 선택된) 객체
    active_object = bpy.context.view_layer.objects.active

    if active_object and active_object.type == 'ARMATURE' and active_object in selected_armatures:
        parent_armature = active_object
        child_armatures = [armature for armature in selected_armatures if armature != parent_armature]
    else:
        parent_armature = None
        child_armatures = []

    # 데이터 업데이트
    props.parent_armature = parent_armature
    props.child_armature_names.clear()
    for armature in child_armatures:
        item = props.child_armature_names.add()
        item.name = armature.name

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
        row.label(text=props.parent_armature.name if props.parent_armature else "None")
        
        # Child Armatures
        box = layout.box()
        row = box.row()
        row.label(text="Child Armatures:")
        for item in props.child_armature_names:
            box.label(text=item.name)

        # Root Bone Selection
        if props.parent_armature:
            box = layout.box()
            row = box.row()
            row.label(text="Root Bone:")
            row.prop_search(props, "root_bone", props.parent_armature.pose, "bones", text="")

        # Traverse Mode Selection
        box = layout.box()
        box.label(text="Traversal Mode:")
        box.prop(props, "traverse_mode", expand=True)

        # Apply Button
        if props.parent_armature and props.child_armature_names and props.root_bone:
            layout.operator("object.copy_transforms_multi_armature", text="Apply Copy Transforms", icon='CHECKMARK')
        else:
            layout.label(text="Complete all selections to apply", icon='ERROR')

# ----------------- Register -----------------
classes = [
    CopyTransformsProperties,
    OBJECT_OT_copy_transforms_operator,
    VIEW3D_PT_copy_transforms_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.copy_transforms_props = bpy.props.PointerProperty(type=CopyTransformsProperties)
    bpy.app.handlers.depsgraph_update_post.append(update_armature_selection)


def unregister():
    if update_armature_selection in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_armature_selection)
    del bpy.types.Scene.copy_transforms_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
