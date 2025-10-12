# Lesson 3: Dynamic SkyDome

With a skydome it is possible to achieve a variety of dynamic effects. One such effect is the ability to change the color of the sky dynamically. Let's start by adding this feature to our fragment shader. Open `Sky.frag.glsl` and make the following changes:
```glsl
#version 140

in vec2 uv;

uniform sampler2D p3d_Texture0;
uniform vec4 horizonColor;
uniform vec4 zenithColor;

out vec4 p3d_FragColor;


void main() {
    // Calculate base color
    vec4 baseColor = horizonColor;
    vec4 colorMask = texture(p3d_Texture0, uv);
    baseColor = mix(baseColor, zenithColor, colorMask.r);

    // Calculate final color
    p3d_FragColor = baseColor;
}
```

These changes will cause the horizon and zenith colors to be obtained from shader inputs and the sky texture will be a color mask which determines color progression from horizon to zenith instead of a diffuse texture. Next we need to rewrite `sky.py` like this:
```glsl
from panda3d.core import (
    DepthTestAttrib,
    OmniBoundingVolume,
    Shader
)


# Classes
# =======
class SkyDome(object):
    sky_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )

    def __init__(self, horizon, zenith):
        # Set background color
        base.win.set_clear_color(horizon)

        # Load skydome mesh
        self.skydome = base.loader.load_model("meshes/DynamicSkyDome.gltf")
        self.skydome.find("**/DynamicSkyDome").node().set_bounds(OmniBoundingVolume())
        self.skydome.set_shader(self.sky_shader)
        self.set_horizon_color(horizon)
        self.set_zenith_color(zenith)
        self.skydome.set_attrib(DepthTestAttrib.make(DepthTestAttrib.M_less_equal))
        self.skydome.reparent_to(base.render)

    def set_horizon_color(self, color):
        self.skydome.set_shader_input("horizonColor", color)

    def set_zenith_color(self, color):
        self.skydome.set_shader_input("zenithColor", color)
```

Since our colors now come directly from shader inputs rather than a texture, we no longer need to convert our background color to sRGB. We also have methods that allow us to change the sky colors on the fly. We also need to change how we create our sky in `main.py`:
```python
# Create skydome
self.skydome = SkyDome(
    Vec4(1, .5, .1, 1),
    Vec4(0, .61, 1, 1)
)
```

If you run your code at this point it should look like this:
![skydome](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/03-dynamic_skydome/screenshots/01-dynamic_skydome.png?raw=true)
![skydome](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/03-dynamic_skydome/screenshots/02-dynamic_skydome.png?raw=true)

With a dynamic sky system like this, we are able to transition the sky color based on time of day or even weather. However, there are other effects we can achieve as well. For example, we can also add clouds that move across the sky. To add clouds, we first need to modify our fragment shader like this:
```glsl
#version 140

in vec2 uv;

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform vec4 horizonColor;
uniform vec4 zenithColor;
uniform vec2 cloudScrollVec;
uniform vec2 cloudScale;
uniform float osg_FrameTime;

out vec4 p3d_FragColor;


void main() {
    // Calculate base color
    vec4 baseColor = horizonColor;
    vec4 colorMask = texture(p3d_Texture0, uv);
    vec4 cloudColor = texture(p3d_Texture1, uv / cloudScale + cloudScrollVec * osg_FrameTime);
    baseColor = mix(baseColor, zenithColor, colorMask.r);
    baseColor = mix(baseColor, cloudColor, cloudColor.a);

    // Calculate final color
    p3d_FragColor = baseColor;
}
```

By sampling a cloud texture and blending it with the base color, we can add clouds to the sky. We scale the cloud UV and scroll it based on a scroll vector and the frame time. Next we need to modify `sky.py`:
```python
from panda3d.core import (
    DepthTestAttrib,
    OmniBoundingVolume,
    Shader,
    TextureStage,
    Vec2
)


# Classes
# =======
class SkyDome(object):
    sky_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )

    def __init__(self, horizon, zenith, cloud_tex):
        # Set background color
        base.win.set_clear_color(horizon)

        # Load skydome mesh
        self.skydome = base.loader.load_model("meshes/DynamicSkyDome.gltf")
        self.skydome.find("**/DynamicSkyDome").node().set_bounds(OmniBoundingVolume())
        self.skydome.set_shader(self.sky_shader)
        self.set_horizon_color(horizon)
        self.set_zenith_color(zenith)
        self.set_cloud_texture(cloud_tex)
        self.set_cloud_scroll_vec(Vec2(.01, 0))
        self.set_cloud_scale(Vec2(1, 1))
        self.skydome.set_attrib(DepthTestAttrib.make(DepthTestAttrib.M_less_equal))
        self.skydome.reparent_to(base.render)

    def set_horizon_color(self, color):
        self.skydome.set_shader_input("horizonColor", color)

    def set_zenith_color(self, color):
        self.skydome.set_shader_input("zenithColor", color)

    def set_cloud_texture(self, tex):
        stage1 = TextureStage("Clouds")
        stage1.set_sort(1)
        self.skydome.set_texture(stage1, tex)

    def set_cloud_scroll_vec(self, vec):
        self.skydome.set_shader_input("cloudScrollVec", vec)

    def set_cloud_scale(self, scale):
        self.skydome.set_shader_input("cloudScale", scale)
```

The new methods allow us to set the new shader uniforms to change the clouds. Make sure you create a new texture stage and set its sort to 1 when setting the cloud texture. This ensures that the cloud texture will be always be texture 1. We also need to modify `main.py` like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file,
    SamplerState,
    Vec2,
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

        # Load textures
        self.cloud_tex = self.loader.load_texture("images/Clouds.png")
        self.cloud_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.cloud_tex.magfilter = SamplerState.FT_linear_mipmap_linear
        self.cloud_tex.wrap_u = SamplerState.WM_repeat
        self.cloud_tex.wrap_v = SamplerState.WM_repeat

        # Create skydome
        self.skydome = SkyDome(
            Vec4(1, .5, .1, 1),
            Vec4(0, .61, 1, 1),
            self.cloud_tex
        )
        self.skydome.set_cloud_scale(Vec2(.5, .5))


# Entry Point
if __name__ == "__main__":
    SkyDemo().run()
```

If you run your code at this point, you should see clouds which slowly scroll from east to west:
![clouds](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/03-dynamic_skydome/screenshots/03-clouds.png?raw=true)
![clouds](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/03-dynamic_skydome/screenshots/04-clouds.png?raw=true)

Sometimes we don't want clouds in the sky though. To achieve this, simply use a fully transparent cloud texture. Now that we have clouds, let's also add a sun and moon. For simplicity, we will put the sun and moon on a single texture for celestial bodies. We will need to modify our fragment shader like this:
```glsl
#version 140

in vec2 uv;

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform vec4 horizonColor;
uniform vec4 zenithColor;
uniform vec2 cloudScrollVec;
uniform vec2 cloudScale;
uniform vec2 celestialScrollVec;
uniform float osg_FrameTime;

out vec4 p3d_FragColor;


void main() {
    // Calculate base color
    vec4 baseColor = horizonColor;
    vec4 colorMask = texture(p3d_Texture0, uv);
    vec4 cloudColor = texture(p3d_Texture1, uv / cloudScale + cloudScrollVec * osg_FrameTime);
    vec4 celestialColor = texture(p3d_Texture2, uv / vec2(2, 1) + celestialScrollVec * osg_FrameTime);
    baseColor = mix(baseColor, zenithColor, colorMask.r);
    baseColor = mix(baseColor, celestialColor, celestialColor.a);
    baseColor = mix(baseColor, cloudColor, cloudColor.a);

    // Calculate final color
    p3d_FragColor = baseColor;
}
```

It's important to blend the celestial texture before the clouds in order for the clouds to appear over the sun or moon. The celestial scroll vector controls how the celestial bodies move across the sky. We also have to modify `sky.py` like this:
```python
from panda3d.core import (
    DepthTestAttrib,
    OmniBoundingVolume,
    Shader,
    TextureStage,
    Vec2
)


# Classes
# =======
class SkyDome(object):
    sky_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )

    def __init__(self, horizon, zenith, cloud_tex, celestials_tex):
        # Set background color
        base.win.set_clear_color(horizon)

        # Load skydome mesh
        self.skydome = base.loader.load_model("meshes/DynamicSkyDome.gltf")
        self.skydome.find("**/DynamicSkyDome").node().set_bounds(OmniBoundingVolume())
        self.skydome.set_shader(self.sky_shader)
        self.set_horizon_color(horizon)
        self.set_zenith_color(zenith)
        self.set_cloud_texture(cloud_tex)
        self.set_cloud_scroll_vec(Vec2(.01, 0))
        self.set_cloud_scale(Vec2(1, 1))
        self.set_celestial_texture(celestials_tex)
        self.set_celestial_scroll_vec(Vec2(.001, 0))
        self.skydome.set_attrib(DepthTestAttrib.make(DepthTestAttrib.M_less_equal))
        self.skydome.reparent_to(base.render)

    def set_horizon_color(self, color):
        self.skydome.set_shader_input("horizonColor", color)

    def set_zenith_color(self, color):
        self.skydome.set_shader_input("zenithColor", color)

    def set_cloud_texture(self, tex):
        stage1 = TextureStage("Clouds")
        stage1.set_sort(1)
        self.skydome.set_texture(stage1, tex)

    def set_cloud_scroll_vec(self, vec):
        self.skydome.set_shader_input("cloudScrollVec", vec)

    def set_cloud_scale(self, scale):
        self.skydome.set_shader_input("cloudScale", scale)

    def set_celestial_texture(self, tex):
        stage2 = TextureStage("Celestials")
        stage2.set_sort(2)
        self.skydome.set_texture(stage2, tex)

    def set_celestial_scroll_vec(self, vec):
        self.skydome.set_shader_input("celestialScrollVec", vec)
```

And we need to modify `main.py` as well:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file,
    SamplerState,
    Vec2,
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

        # Load textures
        self.cloud_tex = self.loader.load_texture("images/Clouds.png")
        self.cloud_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.cloud_tex.magfilter = SamplerState.FT_linear_mipmap_linear
        self.cloud_tex.wrap_u = SamplerState.WM_repeat
        self.cloud_tex.wrap_v = SamplerState.WM_repeat

        self.celestials_tex = self.loader.load_texture("images/Celestials.png")
        self.celestials_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.celestials_tex.magfilter = SamplerState.FT_linear_mipmap_linear
        self.celestials_tex.wrap_u = SamplerState.WM_repeat
        self.celestials_tex.wrap_v = SamplerState.WM_repeat

        # Create skydome
        self.skydome = SkyDome(
            Vec4(1, .5, .1, 1),
            Vec4(0, .61, 1, 1),
            self.cloud_tex,
            self.celestials_tex
        )
        self.skydome.set_cloud_scale(Vec2(.5, .5))


# Entry Point
if __name__ == "__main__":
    SkyDemo().run()
```

If you run your code at this point, you should see the sun and moon move slowly across the sky. Only one should be visible at a time:
![sun](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/03-dynamic_skydome/screenshots/05-sun.png?raw=true)
![moon](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/shadeless/sky/03-dynamic_skydome/screenshots/06-moon.png?raw=true)
