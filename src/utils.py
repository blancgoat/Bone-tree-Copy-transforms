import bpy

def validate_armature(obj, context, prop_name):
    """Validate if the selected object is an Armature, otherwise clear it."""
    if obj and obj.type != 'ARMATURE':
        def draw(self, context):
            self.layout.label(text=f"'{obj.name}' is not an Armature object!")
        bpy.context.window_manager.popup_menu(draw, title="Invalid Selection", icon='ERROR')
        setattr(context.scene.copy_transforms_props, prop_name, None)
