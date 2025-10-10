# Lesson 1: Static Skybox

In this tutorial series, I will be teaching how to render various types of skies. The first type of sky we will be learning about is a simple skybox. This is one of the most simple skies you can make. It works by rendering a cube with a cubemap sky texture applied to it. However, we also need the cube to follow the camera. But just the camera's position. Not its rotation. First, download the images we will need for this tutorial:
[https://github.com/Cybermals/panda3d-shader-tutorials/raw/refs/heads/main/shadeless/sky/images.zip](https://github.com/Cybermals/panda3d-shader-tutorials/raw/refs/heads/main/shadeless/sky/images.zip)

Unzip the downloaded archive and you should have the following project structure:
```
project/
    images/
        TestSky-0.png
        TestSky-1.png
        TestSky-2.png
        TestSky-3.png
        TestSky-4.png
        TestSky-5.png
```

Each of the 6 images corresponds to 1 side of a cube in the following order:
0. right
1. left
2. forward
3. back
4. up
5. down

The sample images have text indicating which side of the cube they correspond to and which orientation is correct. Next, we need to create the shaders for our project. Create a folder called `shaders`. Then create a file called `Sky.vert.glsl` in the shaders folder with the following content:
```glsl
#version 140

in vec4 p3d_Vertex;

uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ProjectionMatrix;

out vec3 uv;


void main() {
    // Calculate vertex position
    mat4 skyboxViewMatrix = mat4(mat3(p3d_ViewMatrix));
    gl_Position = p3d_ProjectionMatrix * skyboxViewMatrix * p3d_Vertex;
    gl_Position.z = gl_Position.w;

    // Calculate UV
    uv = p3d_Vertex.xyz;
}
```

And create `Sky.frag.glsl` in the shaders folder with the following content:
```glsl
#version 140

in vec3 uv;

uniform samplerCube p3d_Texture0;

out vec4 p3d_FragColor;


void main() {
    // Calculate final color
    p3d_FragColor = texture(p3d_Texture0, uv);
}
```

Sky shaders work a bit different than normal shaders. The vertex shader discards translation from the view matrix by converting it to a 3x3 matrix and converting it back to a 4x4 matrix. Then it multiplies the vertex through the resulting matrix and the projection matrix. The Z component of the resulting vertex position is then set to the W component. The UV coordinate is the same as the vertex position. The fragment shader samples the cubemap texture and emits the color unchanged.

Now we need to create our skybox. Create a file called `sky.py` in the main project folder with the following code:
```python
from panda3d.core import (
    DepthTestAttrib,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    OmniBoundingVolume,
    Shader
)


# Classes
# =======
class SkyBox(object):
    skybox_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )
    skybox_mesh = None

    def __init__(self, texture):
        # Create skybox mesh
        if self.skybox_mesh is None:
            # Get vertex format
            vtx_format = GeomVertexFormat.get_v3()

            # Allocate vertex data
            vertices = GeomVertexData("Skybox", vtx_format, Geom.UH_static)
            vertices.reserve_num_rows(8)

            # Write vertex data
            vertex = GeomVertexWriter(vertices, "vertex")

            vertex.add_data3(-1, -1, -1)
            vertex.add_data3(1, -1, -1)
            vertex.add_data3(-1, 1, -1)
            vertex.add_data3(1, 1, -1)
            vertex.add_data3(-1, -1, 1)
            vertex.add_data3(1, -1, 1)
            vertex.add_data3(-1, 1, 1)
            vertex.add_data3(1, 1, 1)

            # Allocate primitive data
            triangles = GeomTriangles(Geom.UH_static)
            triangles.reserve_num_vertices(12)

            # Write primitive data
            triangles.add_vertices(4, 5, 1)
            triangles.add_vertices(1, 0, 4)
            triangles.add_vertices(2, 3, 7)
            triangles.add_vertices(7, 6, 2)
            triangles.add_vertices(2, 6, 4)
            triangles.add_vertices(4, 0, 2)
            triangles.add_vertices(1, 5, 7)
            triangles.add_vertices(7, 3, 1)
            triangles.add_vertices(4, 6, 7)
            triangles.add_vertices(7, 5, 4)
            triangles.add_vertices(0, 1, 3)
            triangles.add_vertices(3, 2, 0)

            # Create skybox mesh
            SkyBox.skybox_mesh = Geom(vertices)
            self.skybox_mesh.add_primitive(triangles)

        # Create skybox
        self.skybox = base.render.attach_new_node(GeomNode("Skybox"))
        self.skybox.node().add_geom(self.skybox_mesh)
        self.skybox.node().set_bounds(OmniBoundingVolume())
        self.skybox.set_shader(self.skybox_shader)
        self.skybox.set_texture(texture)
        depth_test_attrib = DepthTestAttrib.make(DepthTestAttrib.M_less_equal)
        self.skybox.set_attrib(depth_test_attrib)
```

The cube mesh only needs to be created once, so we will cache it in a static class variable. The bounding volume must be an omnidirectional bounding volume to ensure that it is always rendered. Also, we need to set the depth test to less than or equal to. Our `main.py` file is pretty simple:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import SamplerState

from sky import SkyBox


# Classes
# =======
class SkyDemo(ShowBase):
    def __init__(self):
        # Call the base constructor
        ShowBase.__init__(self)

        # Load cubemap sky texture
        self.sky_tex = self.loader.load_cube_map("images/TestSky-#.png")
        self.sky_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.sky_tex.magfilter = SamplerState.FT_linear_mipmap_linear

        # Create sky
        self.sky = SkyBox(self.sky_tex)


# Entry Point
if __name__ == "__main__":
    SkyDemo().run()
```

All we have to do is load our cubemap texture, set its min and mag filters to linear mipmap linear, and create our skybox. When loading a cubemap texture you must place a "#" in the path where the image number should be. If we run our code at this point, we should see this:
![skybox](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/01-static_skybox/screenshots/01-static_skybox.png?raw=true)

If you rotate the camera by holding Alt and dragging, you can see more of the skybox:
![skybox](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/01-static_skybox/screenshots/02-static_skybox.png?raw=true)
