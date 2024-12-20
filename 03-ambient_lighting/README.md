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
vec4 applyLighting(vec4 color) {
    // Calculate lighting
    vec4 lighting = p3d_LightModel.ambient * p3d_Material.ambient;

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}
```

This function simply accepts a color, calculates the lighting factor by multiplying the ambient light color by the ambient material color, sets the lighting alpha value to the alpha value of the initial color, and returns the initial color multiplied by the lighting factor. We also need to modify our `main` function to use our new lighting function:
```glsl
void main() {
    // Calculate base color
    vec4 baseColor = vec4(0, .225, .8, 1);

    // Calculate final color
    p3d_FragColor = applyLighting(baseColor);
}
```

If you run your code at this point, you will see that our sphere is now darker:  
![ambient sphere](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/03-ambient_lighting/screenshots/01-ambient-sphere.png?raw=true)

This may seem counter-productive at first. After all, why would light darken the scene? The reason why this happened is because we haven't yet implemented any other types of lighting yet.
