# Lesson 2: Shadeless Rendering

Now that we have a simple scene setup, let's discuss the purpose of custom shaders. In the last lesson, we enabled auto shaders. This causes Panda3D to automatically generate shaders for us. So you may be wondering why we would want to write custom shaders. While it's true that auto shaders are convenient and you can develop entire games using just auto shaders, there are some visual effects that require creating custom shaders. For example, if we needed to assign different textures to different portions of a terrain mesh based on a mask via a technique known as texture splatting, we would need to write custom shaders. Creating realistic water requires custom shaders too. And so does shader-based heightmapped terrain. Therefore, learning to write custom shaders opens up many new possibilities that would otherwise be difficult if not impossible to implement without custom shaders.  

Now that we know the purpose of custom shaders, let's explore what shaders consist of. Shaders consist of multiple stages. The available shader stages as of the time this tutorial was written are vertex shader, fragment shader, geometry shader, tessellation control shader, and tessellation evaluation shader. Out of all these shader stages, the most commonly used are the vertex shader and the fragment shader. For now I will only be teaching how to implement these two shader stages.  

The role of the vertex shader is to transform vertex positions from local space to clip space and perform calculations needed by the next shader stage. The role of the fragment shader is to calculate the color and depth of each fragment that makes up a mesh. By using just these two shader stages we can draw any sort of mesh. For convenience, we can place the code for each shader stage in its own file and load them from disk at runtime. Let's start by creating a `shaders` folder for our shader code. The new folder structure for your project should look like this:
```
project/
    meshes/
        tex/
            ColorGrid.png
        Sphere.egg
    shaders/
    main.py
```

Next let's create our vertex shader. Create `Sphere.vert.glsl` in your `shaders` folder with the following code:
```glsl
#version 140

in vec4 p3d_Vertex;

uniform mat4 p3d_ModelViewProjectionMatrix;


void main() {
    // Calculate vertex position
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
```

The first line defines the version of GLSL we are using. The next few lines define the inputs the shader accepts. Variables preceded by the `in` keyword will receive a different value per vertex. Variables preceded by the `uniform` keyword will receive a different value per mesh. Some inputs are automatically assigned a value by Panda3D, however we can also define custom inputs that we can bind our own values to. In this case we are using 2 values provided by Panda3D called `p3d_Vertex` and `p3d_ModelViewProjectionMatrix`. `p3d_Vertex` will receive the position of each vertex and `p3d_ModelViewProjectionMatrix` will receive the matrix needed to transform our vertex position from local space to clip space. Every shader must also have a `main` function that will be called each time the shader is invoked. This time, all we need to do is multiply our vertex position by our model-view-projection matrix and assign the result to the built-in `gl_Position` output variable.  

Now let's create our fragment shader. Create `Sphere.frag.glsl` in your `shaders` folder with the following code:
```glsl
#version 140

out vec4 p3d_FragColor;


void main() {
    // Calculate fragment color
    p3d_FragColor = vec4(0, .225, .8, 1);
}
```

Yet again, we will start by defining the GLSL version we are using. Variables preceded by the `out` keyword will be assigned an output value by our shader. The `p3d_FragColor` variable will be assigned the color of the fragment being processed. The `main` function for this shader will simply assign `vec4(0, .225, .8, 1)` to `p3d_FragColor`. This will cause the entire mesh to be light blue.  

Now that we have created our shader stages, we need to load our shader and use it. Open `main.py` and add the following code above where you load the sphere mesh in the `__init__` method of your `ShaderDemo` class:
```python
# Load custom shaders
self.sphere_shader = Shader.load(
    Shader.SL_GLSL,
    "shaders/Sphere.vert.glsl",
    "shaders/Sphere.frag.glsl"
)
```

We also need to change our sphere loading code like this:
```python
# Load sphere mesh
self.sphere = self.loader.load_model("meshes/Sphere")
self.sphere.set_pos(0, 5, 0)
self.sphere.set_shader(self.sphere_shader)
self.sphere.reparent_to(self.render)
```

If you run your code now, you should see an unshaded light blue sphere:  
![unshaded sphere](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/02-shadeless_rendering/screenshots/01-unshaded_sphere.png?raw=true)

If your sphere looks the same as before you loaded your custom shader, then most likely there were errors in your shader code. Whenever there are errors in your shader code, Panda3D will print error messages to the terminal regarding what shaders failed to compile as well as why they failed to compile.  

Now that we have a basic shader working, we can proceed to implement lighting calculations.
