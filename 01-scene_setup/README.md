# Lesson 1: Scene Setup

In this tutorial series, I will be teaching you how to create shaders for use with Panda3D. This tutorial assumes that you already understand the basics of using Panda3D. If you have not already, I highly recommend that you complete the following tutorials before proceeding:
* https://docs.panda3d.org/1.10/python/introduction/tutorial/index
* https://arsthaumaturgis.github.io/Panda3DTutorial.io/

Throughout this tutorial series, we will be using a simple scene to practice applying different shaders. So the first thing we are going to do is setup a simple scene we can use. First we need to create a folder for our project. You can name your project folder whatever you want. Next, we need to create a Panda3D application. Let's start by creating a simple window. Create `main.py` with the following code:
```python
from direct.showbase.ShowBase import ShowBase


# Application Class
# =================
class ShaderDemo(ShowBase):
    def __init__(self):
        # Call the base constructor
        ShowBase.__init__(self)


# Entry Point
# ===========
if __name__ == "__main__":
    ShaderDemo().run()

```

If you run your code at this point, you should see a window like this:
![window screenshot](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/01-scene_setup/screenshots/01-window.png?raw=true)

Next we are going to need a mesh to display. We will be using a sphere mesh to help visualize the effect different shaders have on the surface of a mesh. For convenience, I have prepared a simple sphere mesh with a color UV grid texture for you to use. Use the following link to download the mesh:  
sphere download link  

After you have downloaded the sphere mesh, unzip it and place it into your project folder so you end up with a folder structure like this:
```
project/
    meshes/
        tex/
            ColorGrid.png
        Sphere.egg
    main.py
```

Now let's add the sphere to our scene. In the `__init__` method of your `ShaderDemo` class, add the following code:
```python
# Load sphere mesh
self.sphere = self.loader.load_model("meshes/Sphere")
self.sphere.set_pos(0, 5, 0)
self.sphere.reparent_to(self.render)
```

If you run your code at this point, you should see a textured sphere like this:
![sphere](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/01-scene_setup/screenshots/02-sphere.png?raw=true)
