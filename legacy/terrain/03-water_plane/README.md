# Lesson 3: Water Plane

In this lesson, I will be showing you how to create a simple water plane with a solid color on it. This water plane will be used in subsequent lessons to implement realistic water gradually over the next few lessons. Since realistic water requires more than just a simple plane and some shaders, we will place our new water system in a separate file called `water.py`. Let's start by creating a `WaterPlane` class in our new file:
```python
from panda3d.core import (
    Vec3
)


class WaterPlane(object):
    def __init__(self, pos=Vec3(), heading=0, scale=Vec3(1, 1, 1)):
        pass
```

The constructor of our water plane will accept a position, a heading, and a scale. However, you may be wondering why we only accept heading instead of heading, pitch, and roll for rotation. The reason we are doing this is because the type of water system we will be implementing only supports rotation around the Z-axis. Now that we have a basic skeleton for our water plane, let's create the geometry for our plane. One way we could do this is to make a plane model in Blender and load it in our code. However, since a plane is a very simple geometric shape, we will instead just generate the whole plane via code this time. Let's modify our `water.py` file like this:
```python
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    Vec3
)


# Classes
# =======
class WaterPlane(object):
    plane_mesh = None

    def __init__(self, pos=Vec3(), heading=0, scale=Vec3(1, 1, 1)):
        # Initialize plane mesh if necessary
        if self.plane_mesh is None:
            # Get V3N3T2 format
            vtx_format = GeomVertexFormat.get_v3()

            # Allocate vertex data
            vertices = GeomVertexData("WaterPlane", vtx_format, Geom.UH_static)
            vertices.reserve_num_rows(4)

            # Write vertex data
            vertex = GeomVertexWriter(vertices, "vertex")
            vertex.add_data3(-1, 1, 0)
            vertex.add_data3(1, 1, 0)
            vertex.add_data3(-1, -1, 0)
            vertex.add_data3(1, -1, 0)

            # Allocate primitive data
            triangles = GeomTriangles(Geom.UH_static)
            triangles.reserve_num_vertices(6)

            # Write primitive data
            triangles.add_vertices(0, 2, 1)
            triangles.add_vertices(1, 2, 3)

            # Create plane mesh
            WaterPlane.plane_mesh = Geom(vertices)
            self.plane_mesh.add_primitive(triangles)

        # Create water plane
        self.plane = base.render.attach_new_node(GeomNode("WaterPlane"))
        self.plane.node().add_geom(self.plane_mesh)
        self.plane.set_pos(pos)
        self.plane.set_h(heading)
        self.plane.set_scale(scale)
```

For starters, we added a static `plane_mesh` variable to our water plane class. This variable will be used to cache our plane mesh so it can be reused if we have a scene with multiple water planes instead of needing to regenerate the same geometry over and over. If the `plane_mesh` variable is `None`, then we will generate the plane mesh for our water plane. The first thing we must do to generate the plane mesh is to choose a vertex format. In this case, we only need vertex positions because we will be generating surface normals in our water shaders later. Therefore we will use the vertex format "v3" which we can fetch as a predefined vertex format via the `get_v3` method of the `GeomVertexFormat` class. Next we need to allocate memory to hold the vertices for our plane mesh. We first create a `GeomVertexData` object from our chosen vertex format with a usage hint of `Geom.UH_static`. The static usage hint indicates that we intend to send our vertex data to the GPU once and use it many times without changing it. We will then call `reserve_num_rows` to allocate enough memory for the 4 vertices of our plane mesh. Afterwards, we can create a `GeomVertexWriter` object that will write vertex positions to our vertex data object. For each vertex, we simply call `add_data3` with the vertex position passed as parameters. Once we have created our vertex data. We then need to create our primitive data. For a plane mesh, we only need 2 triangles. So we will create a `GeomTriangles` object with a static usage hint, allocate space for 2 triangles (6 vertices), and add our triangles by passing the 3 vertex indices for each triangle to the `add_vertices` method of our triangle primitives object. The last thing we need to do is create a new `Geom` object from our vertex data and add our primitives to it via the `add_primitive` method.

To create a water plane from our water plane mesh, we will need to attach a new `GeomNode` object to `base.render`, and add our mesh to it via the `add_geom` method of the `GeomNode`. Then we can set the position, heading, and scale of our water plane.

Let's test our new water plane next. Open your `main.py` file and modify your imports like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    SamplerState,
    Shader,
    TextureStage,
    Vec2,
    Vec3,
    Vec4
)

from water import WaterPlane
```

Then add the following code after where you create your terrain:
```python
# Load water plane
self.water = WaterPlane(
    Vec3(0, 261, -20),
    scale=Vec3(256, 256, 1)
)
```

If you run your code at this point, you should see a grey plane across the depression in the center of the terrain:  
![water plane](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/legacy/terrain/03-water_plane/screenshots/01-water_plane.png?raw=true)
