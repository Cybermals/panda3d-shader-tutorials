# Lesson 3: Ambient Lighting

In the previous lesson, we successfully created a basic shader. However, our sphere is not currently affected by lighting. In order to fix this, we will need to perform lighting calculations in our shaders. We will start by implementing ambient light. Ambient light simply controls the appearance of all pixels that make up the meshes in our scene. However, you may be wondering why we need to do this. The reason why we need ambient light is to prevent objects in our scene from appearing too dark once we have added other types of lighting. All ambient lighting calculations occur in the fragment shader, so let's start adding ambient lighting to our fragment shader. First we need to add the following uniforms above our output attribute:
```glsl
uniform struct p3d_LightModelParameters {
    vec4 ambient;
} p3d_LightModel;
uniform struct p3d_MaterialParameters {
    vec4 ambient;
    vec4 diffuse;
    vec4 emission;
    vec3 specular;
    float shininess;
    
    vec4 baseColor;
    float roughness;
    float metallic;
    float refractiveIndex;
} p3d_Material;
```

`p3d_LightModel` contains the total color of all ambient light sources in the scene and `p3d_Material` contains all the properties of the material for the mesh being drawn. For convenience, we will add a new function where we will do our lighting calculations:
```glsl
vec4 applyLighting(vec4 albedo) {
    // Apply lighting to initial color
    vec3 ambient = p3d_LightModel.ambient.rgb * albedo.rgb * 
        p3d_Material.refractiveIndex;
    vec3 color = ambient;
    color = color / (color + vec3(1.0));
    return vec4(pow(color, vec3(1.0 / 2.2)), albedo.a);
}
```

This function calculates the product of the ambient light color, the base color (aka. albedo), and the material refractive index. Then it assigns it to a `color` variable which will later be replaced with a different formula. Next it applies tone mapping and gamma correction. This step is necessary because PBR shaders perform calculations in linear space. Since PBR lighting calculations require colors to be in linear space, we will also need a function that converts from sRGB to linear color space:
```glsl
vec4 srgbToLinear(vec4 color) {
    return vec4(pow(color.rgb, vec3(2.2)), color.a);
}
```

We also need to modify our `main` function to convert the base color to linear color space and use our new lighting function:
```glsl
void main() {
    // Calculate base color
    vec4 baseColor = vec4(0.0, .225, .8, 1.0);
    baseColor = srgbToLinear(baseColor);

    // Calculate final color
    p3d_FragColor = applyLighting(baseColor);
}
```

If you run your code at this point, you will see that our sphere is now quite dark:
![ambient sphere](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/03-ambient_lighting/screenshots/01-ambient_sphere.png?raw=true)

In order to get the correct appearance we also need to set the framebuffer to sRGB mode. Create a `settings.prc` file with the following content:
```
framebuffer-srgb 1
```

Then modify your imports like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    load_prc_file,
    PointLight,
    Shader,
    Vec3,
    Vec4
)
```

And add this code at the top of the `__init__` method of your `ShowBase` class above where you call the base constructor:
```python
# Load config file
load_prc_file("settings.prc")
```

Now the sphere should look like this:
srgb framebuffer
