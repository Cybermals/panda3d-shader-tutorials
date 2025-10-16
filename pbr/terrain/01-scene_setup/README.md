# Lesson 1: Scene Setup

In this tutorial series, I will be teaching how to write shaders that are useful for rendering terrain, including water. This tutorial series assumes that you have completed my tutorial series on the basics of creating shaders for Panda3D. If you have not already, I recommend that you complete that tutorial series first. Let's start by creating a new project folder and adding `main.py` with the following content:
```python
from direct.showbase.ShowBase import ShowBase


# Application Class
# =================
class TerrainDemo(ShowBase):
    def __init__(self):
        # Call base constructor
        ShowBase.__init__(self)


# Entry Point
# ===========
if __name__ == "__main__":
    TerrainDemo().run()
```

Now we need to load some terrain to test our shaders on. For this tutorial series we will generate our terrain from a grayscale heightmap image. First, download the following zip file:
[https://github.com/Cybermals/panda3d-shader-tutorials/raw/refs/heads/main/pbr/terrain/images.zip](https://github.com/Cybermals/panda3d-shader-tutorials/raw/refs/heads/main/pbr/terrain/images.zip)

Then unpack the zip file so your project structure looks like:
```
project/
    images/
        Blank.png
        ColorMask.png
        Dirt.png
        Grass.png
        Heightmap.png
        Heightmap2.png
        Rock.png
        WaterDUDV.png
        WaterNormal.png
    main.py
```

Next, we need to add the following imports to the top of `main.py`:
```python
from panda3d.core import (
    GeoMipTerrain,
    Material,
    Vec4
)
```

Before we load our terrain, we will need to create a material for it:
```python
# Create materials
terrain_mat = Material("Terrain")
terrain_mat.set_base_color(Vec4(0, .5, 0, 1))
terrain_mat.set_metallic(0)
terrain_mat.set_emission(Vec4(0, 0, 0, 1))
terrain_mat.set_roughness(.8)
terrain_mat.set_refractive_index(1.5)
```

Afterwards, we can load our terrain with the following code:
```python
# Load terrain
self.terrain = GeoMipTerrain("Terrain")
self.terrain.set_heightfield("images/Heightmap.png")
self.terrain.set_block_size(32)
self.terrain.set_focal_point(self.camera)

self.terrain.get_root().set_sz(128)
self.terrain.get_root().set_pos(-256, 0, -64)
self.terrain.get_root().set_material(terrain_mat)

self.terrain.generate()
self.terrain.get_root().reparent_to(self.render)
```

The `GeoMipTerrain` class generates terrain from a grayscale heightmap image loaded via the `set_heightmap` method. It will generate equal sized blocks of terrain based on the block size we set. Larger block sizes yield less meshes, but increase the time needed to build the mesh for each block. Blocks closest to the focal point will have the highest level of detail (LOD). We can call the `get_root` method to get the nodepath which the terrain blocks are parented to. Set the scale of the terrain root to control the size of the terrain. The Z scale determines the maximum height of the terrain. The origin of the terrain is in the lower left corner at the lowest elevation. So you may want to set the position of the terrain root as well. We also need to set the material for the terrain. Make sure you call the `generate` method of the terrain and reparent the terrain root to the root of the scene graph or you won't see anything.

If you run your code at this point, you will see a solid white mass:
![shadeless terrain](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/terrain/01-scene_setup/screenshots/01-shadeless_terrain.png?raw=true)

Let's improve the appearance of our terrain by initializing `panda3d-simplepbr` and setting up some basic lighting. Modify your imports like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    GeoMipTerrain,
    Material,
    Vec4
)
import simplepbr
```

Then add the following lines above where you load the terrain:
```python
# Init shaders
simplepbr.init()

# Setup lighting
self.ambient_light = self.render.attach_new_node(AmbientLight("AmbientLight"))
self.ambient_light.node().set_color(Vec4(.2, .2, .2, 1))
self.render.set_light(self.ambient_light)

self.sun = self.render.attach_new_node(DirectionalLight("Sun"))
self.sun.set_hpr(45, -45, 0)
self.render.set_light(self.sun)
```

Now if you run your code, you should be able to see the terrain contour better:  
![shaded terrain](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/terrain/01-scene_setup/screenshots/02-shaded_terrain.png?raw=true)

However, if you move the camera around with the mouse you will notice that the terrain detail remains low on the opposite side of the terrain:
![static terrain lod](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/terrain/01-scene_setup/screenshots/03-static_lod.png?raw=true)

To fix this, we need to enable dynamic LOD by creating a task which calls the `update` method of the terrain. Add the following method to your showbase class:
```python
def update(self, task):
    # Update terrain
    self.terrain.update()
    return task.cont
```

And then add the following code to your `__init__` method:
```python
# Add update task
self.task_mgr.add(self.update, "update")
```

If you run your code now, you should see the terrain detail change as you move the camera around:
![dynamic terrain lod](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/terrain/01-scene_setup/screenshots/04-dynamic_lod.png?raw=true)

However, our terrain still has no texture at this point. We could simply apply a single texture to the terrain surface, but doing so would limit what we could do with our terrain. However, there is a technique we can use to use multiple textures on the same terrain to achieve a high quality for our terrain appearance.
