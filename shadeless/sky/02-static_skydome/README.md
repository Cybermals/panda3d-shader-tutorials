# Lesson 2: Static Skydome

Due to their simplicity, skyboxes are great for many types of projects. However, there are some effects which won't well with a skybox. For example, dynamic skies with moving clouds and/or celestial bodies tend to work better on a dome or sphere. In this lesson, we will implement a static skydome. Let's start by creating `sky.py` with the following content:
```python
# Classes
# =======
class SkyDome(object):
    def __init__(self, horizon):
        # Set background color
        base.win.set_clear_color(pow(horizon, 2.2 / 1))
```

In order for a skydome to work properly we need to set the background color of the window so it matches the color of the horizon. This will help the edges of the skydome blend seamlessly with the skydome texture. However, the texture for our skydome is sRGB. Therefore we will need to also convert our horizon color to sRGB so we can use an sRGB framebuffer. Next we need to create `main.py` with the following content:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file,
    Vec4
)

from sky import SkyDome


# Classes
# =======
class SkyDemo(ShowBase):
    def __init__(self):
        # Load config file
        load_prc_file("settings.prc")

        # Call the base constructor
        ShowBase.__init__(self)

        # Create skydome
        self.skydome = SkyDome(Vec4(0, .61, 1, 1))


# Entry Point
if __name__ == "__main__":
    SkyDemo().run()
```

We also need to create `settings.prc` with the following content:
```
framebuffer-srgb 1
```

If you run your code at this point, you should see this:
![sky background](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/02-static_skydome/screenshots/01-window_background.png?raw=true)

Since a dome is a more complex shape than a cube, we will be using a skydome mesh which I have already prepared. Download the following mesh archive:
[https://github.com/Cybermals/panda3d-shader-tutorials/raw/refs/heads/main/shadeless/sky/meshes.zip](https://github.com/Cybermals/panda3d-shader-tutorials/raw/refs/heads/main/shadeless/sky/meshes.zip)

Next unzip the archive. You should have a project structure like this:
```
project/
    meshes/
        SkyDome.gltf
```

Then we need to create a `shaders` folder. Inside the shaders folder, create `Sky.vert.glsl` with the following content:
```glsl
#version 140

in vec4 p3d_Vertex;
in vec3 p3d_MultiTexCoord0;

uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ProjectionMatrix;

out vec2 uv;


void main() {
    // Calculate vertex position
    mat4 skyboxViewMatrix = mat4(mat3(p3d_ViewMatrix));
    gl_Position = p3d_ProjectionMatrix * skyboxViewMatrix * p3d_Vertex;
    gl_Position.z = gl_Position.w;

    // Calculate UV
    uv = p3d_MultiTexCoord0.xy;
}
```

And we also need to create `Sky.frag.glsl` with the following content:
```glsl
#version 140

in vec2 uv;

uniform sampler2D p3d_Texture0;

out vec4 p3d_FragColor;


void main() {
    // Calculate final color
    p3d_FragColor = texture(p3d_Texture0, uv);
}
```

The key differences between the skybox and skydome shaders are that the skydome calculates normal 2D UV coordinates and the texture type is 2D instead of a cubemap. Next we can modify our `SkyDome` class like this:
```python
class SkyDome(object):
    sky_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )

    def __init__(self, horizon):
        # Set background color
        base.win.set_clear_color(pow(horizon, 2.2 / 1))

        # Load skydome mesh
        self.skydome = base.loader.load_model("meshes/SkyDome.gltf")
        self.skydome.find("**/SkyDome").node().set_bounds(OmniBoundingVolume())
        self.skydome.set_shader(self.sky_shader)
        self.skydome.set_attrib(DepthTestAttrib.make(DepthTestAttrib.M_less_equal))
        self.skydome.reparent_to(base.render)
```

Here we load the sky shader once, load the skydome mesh, set the bounds for the skydome to an omnidirectional bounding volume, set the shader, set the depth test to less than or equal to, and reparent the skydome mesh to the root of the scenegraph. This will cause the skydome to follow the camera position and always be visible. If you run your code at this point, you should notice a subtle gradient between the horizon and zenith:
![skydome](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/02-static_skydome/screenshots/02-static_skydome.png?raw=true)
![skydome](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/02-static_skydome/screenshots/03-static_skydome.png?raw=true)
