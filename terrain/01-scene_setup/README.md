# Lesson 1: Scene Setup

In this tutorial series, I will be teaching how to write shaders that are useful for rendering terrain, including water. Let's start by creating a new project folder and adding `main.py` with the following content:
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

Now we need to load some terrain to test our shaders on. For this tutorial series we will be using a simple terrain mesh. In a production grade project, you will need to decide what sort of terrain system to use based on the properties of the terrain. Download the terrain meshes from the following URL:
terrain meshes

Then unpack the zip file so your project structure looks like:
```
project/
    meshes/
        Terrain.egg
        Water.egg
    main.py
```

Next, we can load the terrain mesh by adding the following code to the `__init__` method of our `TerrainDemo` class:
```python
# Load terrain
self.terrain = self.loader.load_model("meshes/Terrain")
self.terrain.set_scale(256, 256, 256)
self.terrain.set_pos(0, 261, 0)
self.terrain.reparent_to(self.render)
```

If we run your code at this point, you will see a solid white mass:  
![shadeless terrain](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/01-scene_setup/screenshots/01-shadeless_terrain.png?raw=true)