# Lesson 6: Distortion

In the last lesson, we successfully added realistic reflection and refraction to our water plane. However, our water currently looks completely still. There are no ripples. Let's fix that by adding some distortion to our water. In order to add distortion, we will need to displace the UV coordinates used for sampling our reflection and refraction textures. However, we don't want to just use some sort of constant. Instead we will use something known as a DUDV map. A DUDV map is a texture where the red and green color channels are used to represent displacement values. Yellow is neutral, increasing/decreasing red shifts right/left, and increasing/decreasing green shifts up/down. For this lesson, I have supplied a DUDV map in the images archive we unpacked in a previous lesson. Let's start by adding a new uniform to our fragment shader:
```glsl
uniform sampler2D p3d_Texture2;
```

We also need to add some additional calculations after the part where we calculate our reflection and refraction UVs:
```glsl
// Apply distortion
vec2 distortedUV = texture(p3d_Texture2, vec2(uv.x, uv.y)).rg * .1;
distortedUV = uv + vec2(distortedUV.x, distortedUV.y);
vec2 totalDistortion = (texture(p3d_Texture2, distortedUV).rg * 2 - 1) * .02;

refractUV += totalDistortion;
refractUV = clamp(refractUV, .001, .999);

reflectUV += totalDistortion;
reflectUV.x = clamp(reflectUV.x, -.999, -.001);
reflectUV.y = clamp(reflectUV.y, .001, .999);
```

Next, we need to load our DUDV map and add an additional texture stage for it. Add the following code above where you create your plane from the plane mesh:
```python
# Load textures
self.dudv_map_tex = base.loader.load_texture("images/WaterDUDV.png")
self.dudv_map_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.dudv_map_tex.magfilter = SamplerState.FT_linear_mipmap_linear
```

And modify your texture configuration like this:
```python
stage1 = TextureStage("ReflectionTex")
stage2 = TextureStage("DUDVMap")

self.plane.set_texture(self.refract_tex)
self.plane.set_texture(stage1, self.reflect_tex)
self.plane.set_texture(stage2, self.dudv_map_tex)
```

If you run your code now, you should see some distortion on the surface of the water now:  
![distortion](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/terrain/06-distortion/screenshots/01-distortion.png?raw=true)

Now let's make the water move. To do this, we can use the `osg_FrameTime` uniform. It receives the current frame time from Panda3D and we can add it to our UV coordinates to make them scroll. We will also add a uniform for controlling the speed of the scrolling animation. First we need to add some new uniforms to our fragment shader:
```glsl
uniform float osg_FrameTime;
uniform float waveSpeed;
```

Then we will modify our distortion calculations like this:
```glsl
// Apply distortion
vec2 distortedUV = texture(p3d_Texture2, vec2(uv.x + osg_FrameTime * waveSpeed, uv.y)).rg * .1;
distortedUV = uv + vec2(distortedUV.x, distortedUV.y + osg_FrameTime * waveSpeed);
vec2 totalDistortion = (texture(p3d_Texture2, distortedUV).rg * 2 - 1) * .02;

refractUV += totalDistortion;
refractUV = clamp(refractUV, .001, .999);

reflectUV += totalDistortion;
reflectUV.x = clamp(reflectUV.x, -.999, -.001);
reflectUV.y = clamp(reflectUV.y, .001, .999);
```

We also need to set the wave speed uniform in our water plane class:
```python
self.plane.set_shader_input("waveSpeed", .01)
```

Let's also give our water more of a blue tint by adding this code where we calculate the base color of our water:
```glsl
baseColor = mix(baseColor, vec4(0, .225, .5, 1), .2);
```

If you run the code now, you should see the distortions scrolling across the water plane.
