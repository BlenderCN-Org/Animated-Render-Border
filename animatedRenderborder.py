import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

if len(bpy.app.handlers.frame_change_pre)>0:
    bpy.app.handlers.frame_change_pre.remove(bpy.app.handlers.frame_change_pre[0])



bpy.types.Scene.mesh_objects = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

bpy.context.scene.mesh_objects.clear()
for object in bpy.context.scene.objects:
    if object.type == "MESH":
        meshAdd = bpy.context.scene.mesh_objects.add()
        meshAdd.name = object.name



#######Update functions########################################################



def fakeUpdate(self,context):
    
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)    
    
    

def trackUpdate(self,context):
    
    scene = bpy.context.scene
        
    if scene.animated_render_border_type == "Group":
        if scene.animated_render_border_group == "":
            scene.render.use_border = False
            #print("border set to false as type is group and group is blank")
        else:
            scene.render.use_border = True
            scene.frame_set(bpy.context.scene.frame_current)
            #print("border set to true as type is group and group is not blank")
    else:
        if scene.animated_render_border_object == "":
            scene.render.use_border = False
            #print("border set to false as type is object and object is blank")
        else:
            scene.render.use_border = True
            scene.frame_set(bpy.context.scene.frame_current)        
            #print("border set to true as type is obejct and object is not blank")
                


#########Properties###########################################################



bpy.types.Scene.animated_render_border_object = bpy.props.StringProperty(description = "The object to track", update=trackUpdate)
bpy.types.Scene.animated_render_border_group = bpy.props.StringProperty(description = "The group to track", update=trackUpdate)
bpy.types.Scene.animated_render_border_type = bpy.props.EnumProperty(description = "The type of tracking to do, objects or groups", items=[("Object","Object","Object"),("Group","Group","Group")], update=trackUpdate)
bpy.types.Scene.animated_render_border_use_bounding_box = bpy.props.BoolProperty(default=True, description="Use object's bounding box (less reliable, quicker) or object's vertices for boundary checks", update=fakeUpdate)
bpy.types.Scene.animated_render_border_margin = bpy.props.IntProperty(default=3, description="Add a margin around the object's bounds", update=fakeUpdate)



#########Frame Handler########################################################



scene = bpy.context.scene

cam = bpy.data.objects['Camera']

#wm = obj.matrix_world #Vertices will be in local space unless multiplied by the world matrix

#objs = ['Cube','Suzanne']



def animate_render_border(scene):
    objs = [] 
    if scene.animated_render_border_type == "Object": 
        objs = [scene.animated_render_border_object]
    else:
        for object in bpy.data.groups[scene.animated_render_border_group].objects:    
            if object.type == "MESH":
                objs.append(object.name)
    
    #verts = (vert.co for vert in obj.data.vertices)
    #verts = (Vector(vert) for vert in obj.bound_box)  #couldn't get this to work for multiple objects
    
    #coords_2d = [world_to_camera_view(scene, cam, wm*coord) for coord in verts]
    
    coords_2d = []
    
    for obj in objs:
        
        verts = []
        if scene.animated_render_border_use_bounding_box:
            for corner in bpy.data.objects[obj].bound_box:
                verts.append(Vector(corner))
        else:
            for vert in bpy.data.objects[obj].data.vertices:
                verts.append(vert.co)
                
        wm = bpy.data.objects[obj].matrix_world     
        for coord in verts:
            coords_2d.append(world_to_camera_view(scene, cam, wm*coord))
    

    # 2d data printout:
    #rnd = lambda i: round(i)

    minX = 1
    maxX = 0
    minY = 1
    maxY = 0

    #print("")
    #print('x,y')
    for x, y, distance_to_lens in coords_2d:
        
        if x<minX:
            minX = x
        
        if x>maxX:
            maxX = x
        
        if y<minY:
            minY = y
        
        if y>maxY:
            maxY = y                 
            
        #print(round(x,3),round(y,3))  
    
    margin = bpy.context.scene.animated_render_border_margin
        
    bpy.context.scene.render.border_min_x = minX - (margin/100)
    bpy.context.scene.render.border_max_x = maxX + (margin/100)
    bpy.context.scene.render.border_min_y = minY - (margin/100)
    bpy.context.scene.render.border_max_y = maxY + (margin/100)  


bpy.app.handlers.frame_change_pre.append(animate_render_border)



###########UI################################################################



class AnimatedRenderBorderPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Animated Render Border"
    bl_idname = "RENDER_PT_animated_render_border"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(scene, "animated_render_border_type",expand=True)
        row = layout.row()
        if scene.animated_render_border_type == "Object":
            row.label(text="Mesh object to track:")
            row = layout.row()
            row.prop_search(scene, "animated_render_border_object", scene, "mesh_objects", text="", icon="OBJECT_DATA") #Where my property is, name of property, where list I want is, name of list
        else:
            row.label(text="Group to track:")
            row = layout.row()
            row.prop_search(scene, "animated_render_border_group", bpy.data, "groups", text="")
        
        row.prop(scene, "animated_render_border_margin", text="Margin")    
        row = layout.row()
        row.prop(scene, "animated_render_border_use_bounding_box", text="Use Bounding Box")
        row = layout.row()
        row.prop(bpy.data.objects[scene.animated_render_border_object], "show_bounds", text="Draw Bounding Box")
        


def register():
    bpy.utils.register_class(AnimatedRenderBorderPanel)


def unregister():
    bpy.utils.unregister_class(AnimatedRenderBorderPanel)


if __name__ == "__main__":
    register()
