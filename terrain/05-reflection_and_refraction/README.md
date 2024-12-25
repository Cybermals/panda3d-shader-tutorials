# Lesson 5: Reflection and Refraction

In this lesson, I will show you how to add reflection and refraction to our water plane. In order to do this, we will need to render the scene to 2 textures. Let's start by discussing how this will work. When looking at the water, objects below the water will get refracted on the surface of the water:  
![refraction diagram](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/diagrams/01-refraction.png?raw=true)

And objects above the water will get reflected on the surface of the water:  
![reflection diagram](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/diagrams/02-reflection.png?raw=true)

We can create a refraction texture by rendering the scene from the viewpoint of the main camera, however we must use a slightly different approach for rendering the reflection texture. In order to capture the objects above the water, we will need to render the scene from a camera below the water and looking up as depicted in this diagram:  
![reflection camera](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/diagrams/03-reflection_camera.png?raw=true)

The first thing we will need to do, is to setup 2 texture buffers we can use to render our reflection and refraction textures. Modify your imports like this:
```python
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GraphicsOutput,
    Material,
    SamplerState,
    Shader,
    Texture,
    Vec3,
    Vec4
)
```

And add the following code below where you create your water material:
```python
# Get the default camera lens
cam_lens = base.cam.node().get_lens()

# Create refraction buffer. Using (0, 0) for the size indicates that the size of the buffer should
# be synced with the main window.
self.refract_buf = base.win.make_texture_buffer("WaterRefractionBuffer", 0, 0)
self.refract_buf.set_sort(-100)
self.refract_buf.add_render_texture(
    Texture("RefractionDepth"),
    GraphicsOutput.RTM_bind_or_copy,
    GraphicsOutput.RTP_depth
)
self.refract_tex = self.refract_buf.get_texture()
self.refract_depth_tex = self.refract_buf.get_texture(1)
self.refract_tex.wrap_u = SamplerState.WM_repeat
self.refract_tex.wrap_v = SamplerState.WM_repeat

self.refract_cam = base.make_camera(self.refract_buf, lens=cam_lens)
self.refract_cam.reparent_to(base.render)

# Create reflection buffer. Using (0, 0) for the size indicates that the size of the buffer should
# be synced with the main window.
self.reflect_buf = base.win.make_texture_buffer("WaterReflectionBuffer", 0, 0)
self.reflect_buf.set_sort(-100)
self.reflect_tex = self.reflect_buf.get_texture()
self.reflect_tex.wrap_u = SamplerState.WM_repeat
self.reflect_tex.wrap_v = SamplerState.WM_repeat

self.reflect_cam = base.make_camera(self.reflect_buf, lens=cam_lens)
self.reflect_cam.reparent_to(base.render)
```

We use the `make_texture_buffer` method of the main window to create a texture buffer. Passing 0 for the width and height causes the size to be the same as the main window. Setting the sort order to a negative value causes the texture buffers to be rendered to before the main window each frame. We need to add a depth texture to our refraction buffer so we can use the depth values in later calculations. We also need to get each of the textures we are rendering to and set them to repeat. Then we need to create a camera that will be used to render each buffer. We need to use the same lens as the main camera for both of our new cameras. and we also have to reparent our new cameras to the root of the scene graph. Let's also go to `main.py` and add the following code to the bottom of our constructor to enable the buffer viewer:
```python
# Configure buffer viewer
self.bufferViewer.setPosition("ulcorner")
self.bufferViewer.setCardSize(.5, 0)
self.accept("v", self.bufferViewer.toggleEnable)
```

If you run your code at this point, you can now press V to show the contents of each texture buffer as a card at the top of the window. However, as it is rn our reflection and refraction cameras are not being moved when the main camera moves. Let's fix that next. Inside your water plane class, add the following method:
```python
def update_cameras(self, task):
    # Update refraction and reflection cameras
    self.refract_cam.set_transform(base.camera.get_transform())

    self.reflect_cam.set_transform(base.camera.get_transform())
    cam_height = base.camera.get_z()
    dist = cam_height - self.plane.get_z()
    self.reflect_cam.set_z(self.reflect_cam.get_z() - dist * 2)
    self.reflect_cam.set_p(-self.reflect_cam.get_p())
    self.reflect_cam.set_r(self.reflect_cam.get_r() + 180)
    return task.cont
```

And under the part where you create your texture buffers, add this code:
```python
# Register water camera update task
base.task_mgr.add(self.update_cameras, "update_water_cameras")
```

Now if you run your code, you should see the content of your reflection and refraction textures change as you move the camera around the scene:  
![texture buffers](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/screenshots/01-texture_buffers.png?raw=true)

However, our refraction texture should only contain everything below the water and our reflection texture should only contain everything above the water. To enforce this, we will add custom clipping planes. Start by modifying your imports like this:
```python
from panda3d.core import (
    ClipPlaneAttrib,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GraphicsOutput,
    Material,
    Plane,
    PlaneNode,
    SamplerState,
    Shader,
    Texture,
    Vec3,
    Vec4
)
```

Then add the following code to the bottom of your constructor:
```python
# Configure refraction clipping plane
self.refract_clip_plane = self.plane.attach_new_node(PlaneNode(
    "WaterRefractClipPlane",
    Plane(0, 0, -1, -.001)
))
clip_state = ClipPlaneAttrib.make_default().add_on_plane(self.refract_clip_plane)
self.refract_cam.node().set_initial_state(clip_state)

# Configure reflection clipping plane
self.reflect_clip_plane = self.plane.attach_new_node(PlaneNode(
    "WaterReflectClipPlane",
    Plane(0, 0, 1, -.001)
))
clip_state = ClipPlaneAttrib.make_default().add_on_plane(self.reflect_clip_plane)
self.reflect_cam.node().set_initial_state(clip_state)
```

Now we need to add another uniform to our vertex shader:
```glsl
uniform vec4 p3d_ClipPlane[1];
```

And add the following code to your `main` function:
```glsl
// Calculate clip distance
gl_ClipDistance[0] = dot(vec4(fragPos, 1), p3d_ClipPlane[0]);
```

You will also need to make the same changes to your terrain vertex shader. Once you have made these changes, your reflection and refraction textures should only be rendering part of the scene:  
![clipping planes](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/screenshots/02-clip_planes.png?raw=true)

Now let's apply our reflection and refraction textures to the water plane. We need to start by modifying our imports like this:
```python
from panda3d.core import (
    ClipPlaneAttrib,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GraphicsOutput,
    Material,
    Plane,
    PlaneNode,
    SamplerState,
    Shader,
    Texture,
    TextureStage,
    Vec3,
    Vec4
)
```

Then we need to setup our texture stages after where we set our shader:
```python
stage1 = TextureStage("ReflectionTex")

self.plane.set_texture(self.refract_tex)
self.plane.set_texture(stage1, self.reflect_tex)
```

Next, we need to add 2 new uniforms to our fragment shader:
```glsl
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
```

However, we have not yet done our UV calculations. In order to properly map our reflection and refraction textures to the water plane, we will be using a technique known as projective texture mapping. Instead of using UV coordinates from our geometry data, we will instead generate them in the vertex shader. First, we need to add a new output attribute to our vertex shader:
```glsl
out vec2 uv;
```

And we will calculate it with the following code in our `main` function:
```glsl
// Calculate UV
uv = vec2(p3d_Vertex.x / 2 + .5, p3d_Vertex.y / 2 + .5);
```

Now we can go to our fragment shader and add a new input attribute:
```glsl
in vec2 uv;
```

Then we can calculate the correct UV coordinates for our textures in the `main` function like this:
```glsl
// Calculate refraction and reflection UV coordinates
vec2 texelSize = 1 / vec2(textureSize(p3d_Texture0, 0));
vec2 ndc = gl_FragCoord.xy * texelSize;
vec2 refractUV = vec2(ndc.x, ndc.y);
vec2 reflectUV = vec2(-ndc.x, ndc.y);
```

And afterwards we can use the UV coordinates to sample our reflection and refraction textures so we can mix them like this:
```glsl
// Calculate base color
vec4 refractColor = texture(p3d_Texture0, refractUV);
vec4 reflectColor = texture(p3d_Texture1, reflectUV);

vec4 baseColor = mix(refractColor, reflectColor, .5);
```

Let's also change our material like this:
```python
# Initialize water material if necessary
if self.water_mat is None:
    WaterPlane.water_mat = Material()
    self.water_mat.set_ambient(Vec4(1, 1, 1, 1))
    self.water_mat.set_diffuse(Vec4(.8, .8, .8, 1))
    self.water_mat.set_specular(Vec3(.5, .5, .5))
    self.water_mat.set_shininess(32)
```

If you run your code at this point, you will notice that the reflections look off like in this screenshot:  
![reflection bug](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/screenshots/03-reflection_bug.png?raw=true)
