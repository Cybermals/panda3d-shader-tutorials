# Lesson 6: Fog

In this lesson, we will be exploring fog. Fog can be used to make a scene look foggy, but it can also be used for underwater effects and more. The first thing we need to do is modify our imports in `main.py`:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Fog,
    load_prc_file,
    PointLight,
    Shader,
    Vec3,
    Vec4
)
```

Next we need to add the following code right after the part where we setup our lighting in the `__init__` method of our `ShaderDemo` class:
```python
# Setup fog
self.fog = Fog("Fog")
self.fog.set_color(1, 1, 1)
self.render.set_fog(self.fog)
```

For now we will just set the fog color to white and leave the other settings at their defaults. However, if we try to run our application right now, we will not see any fog. The reason why this happens is because we haven't setup any fog calculations in our shaders. Fog calculations are done in the fragment shader. Let's start by adding an additional uniform `p3d_Fog`:
```glsl
uniform struct p3d_FogParameters {
    vec4 color;
    float density;
    float start;
    float end;
    float scale; // 1.0 / (end - start)
} p3d_Fog;
```

We also need to create a function called `applyFog` that will accept a color and apply fog to it:
```glsl
vec4 applyFog(vec4 color) {
    // If fog is disabled, skip fog calculations
    if(p3d_Fog.start == p3d_Fog.end) {
        return color;
    }

    // Calculate linear fog
    float dist = length(fragPos);
    float fogFactor = (p3d_Fog.end - dist) / (p3d_Fog.end - p3d_Fog.start);
    fogFactor = clamp(fogFactor, 0.0, 1.0);
    return mix(p3d_Fog.color, color, fogFactor);
}
```

Our new function will first check if the `start` and `end` properties of the fog are equal. If they are, then fog is turned off and we will return the initial color unmodified. Otherwise, we will calculate the distance to the fragment position with the `length` function. Next, we will calculate the fog factor by dividing the difference of the fog `end` property and the fragment distance by the differene of the fog `end` and `start` properties. This is known as linear fog. There are other formulas that can be used to calculate the fog factor as well, such as exponential fog. The next thing we must do it clamp the fog factor to the range [0-1]. Last but not least, we need to use the fog factor to mix the fog color and initial color.  

To apply fog to each fragment, we also need to rewrite our `main` function like this:
```glsl
void main() {
    // Calculate base color
    vec4 baseColor = texture(p3d_Texture0, uv);

    // Calculate final color
    p3d_FragColor = applyFog(applyLighting(baseColor));
}
```

If you run your code now, you will see a sphere will a slight foggy appearance. Try holding the Ctrl key and slowing dragging up/down with the mouse to move the camera farther/nearer from the sphere and you will see how the fog changes based on distance from the sphere:
![fog 1](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/06-fog/screenshots/01-fog.png?raw=true)  
![fog 2](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/06-fog/screenshots/02-fog.png?raw=true)  
![fog 3](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/06-fog/screenshots/03-fog.png?raw=true)
