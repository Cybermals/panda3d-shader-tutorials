# Lesson 4: Diffuse Lighting

When light rays strike the surface of an object, part of the light gets absorbed into the surface. We can simulate this by using an algorithm known as Blinn-Phong shading. In the following diagram, we see a light source (L) casting a ray (V) onto a surface (S). We also see a vector (N) perpendicular to the surface (S). Ray (V) is known as the light vector and vector (N) is known as the surface normal:  
![diffuse lighting diagram](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/04-diffuse_lighting/diagrams/01-diffuse_lighting.png?raw=true)

In order to determine how much diffuse lighting from a given light source should affect a surface, we need to calculate the angle (T) between the surface normal (N) and the light vector (V). Let's start by calculating the surface normal in our vertex shader. First we need to add another input attribute `p3d_Normal` that will receive the per-vertex surface normal:
```glsl
in vec3 p3d_Normal;
```

We also need to add another uniform `p3d_NormalMatrix` that will receive the normal matrix:
```glsl
uniform mat3 p3d_NormalMatrix;
```

And we will need a new output attribute `normal` that will be used to pass the transformed normal to the fragment shader:
```glsl
out vec3 normal;
```

Now we can rewrite our `main` function like this:
```glsl
void main() {
    // Calculate vertex position and surface normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    normal = p3d_NormalMatrix * p3d_Normal;
}
```

The new line multiplies the per-vertex normal through the normal matrix and assigns it to the `normal` output attribute that will be passed to the fragment shader. Next we need to add a `normal` input attribute to our fragment shader:
```glsl
in vec3 normal;
```

However, when passing the normal from our vertex shader to our fragment shader, the interpolation process which occurs between the two shader stages my cause the length of the normal to no longer equal 1. This will throw off our lighting calculations, so we need to normalize the normal by adding the following lines to the beginning of our lighting function:
```glsl
// Normalize normal
vec3 norm = normalize(normal);
```

Next we need to calculate our light vector (V). The formula used to calculate this vector depends on the type of light source though. A directional light has a direction, but no position. In contrast, a point light has a position, but no direction. Furthermore, a spot light has a position and a direction. Therefore, we must determine which type of light source we are working with and use the correct formula. First we need to add a new uniform `p3d_LightSource` to our fragment shader:
```glsl
uniform struct p3d_LightSourceParameters {
    // Primary light color.
    vec4 color;

    // Light color broken up into components, for compatibility with legacy
    // shaders. These are now deprecated.
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;

    // View-space position. If w=0, this is a directional light, with the xyz
    // being -direction.
    vec4 position;

    // Spotlight-only settings
    vec3 spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;

    // Individual attenuation constants
    float constantAttenuation;
    float linearAttenuation;
    float quadraticAttenuation;

    // constant, linear, quadratic attenuation in one vector
    vec3 attenuation;

    // Shadow map for this light source
    sampler2DShadow shadowMap;

    // Transforms view-space coordinates to shadow map coordinates
    mat4 shadowViewMatrix;
} p3d_LightSource[2];
```

The number in square brackets should be equal to the total number of directional, point, and spot lights in the scene. If the `w` component of a light source's `position` member is equal to 0, then it is a directional light. Otherwise, it is a point or spot light. For now, we will only be covering directional and point lights. To simplify things, let's define separate functions for handling directional and point lights. We will start by defining a function called `calcDirectionalLighting`:
```glsl
vec4 calcDirectionalLighting(int lightIdx, vec3 normal) {
    // Calculate light vector
    vec3 lightVector = normalize(p3d_LightSource[lightIdx].position.xyz);

    // Calculate diffuse lighting
    float nxDir = max(0, dot(normal, lightVector));
    vec4 diffuse = p3d_LightSource[lightIdx].color * nxDir;

    // Calculate total lighting
    return (p3d_LightModel.ambient * p3d_Material.ambient + 
        (diffuse * p3d_Material.diffuse));
}
```

For the given light and normal, this function will first normalize the light vector passed in the `position` member of the light. Next, it will calculate the diffuse factor by calculating the dot product of the normal and light vector. The result will be set to 0 if it is less than 0 via the `max` function. Then we will multiply the color of the given light source by the diffuse factor to get the diffuse color. Afterwards, all we have to do is add the product of the diffuse color and the `diffuse` material property to the product of the ambient light color and the `ambient` material property to get the total color for the given light. We can test our new diffuse lighting by rewriting our `applyLighting` function like this:
```glsl
vec4 applyLighting(vec4 color) {
    // Normalize normal
    vec3 norm = normalize(normal);

    // Calculate lighting
    vec4 lighting = calcDirectionalLighting(0, norm);

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}
```

If you run your code at this point, you should see a blue sphere with diffuse shading:  
![diffuse sphere](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/04-diffuse_lighting/screenshots/01-diffuse_sphere.png?raw=true)

Now that we have some diffuse lighting, our scene has a lot more depth. However, we are currently only handling our directional light. Ideally, we want to handle all of the lights in our scene. In order to do that, we will need to create a function to handle point lights since our other light is one. But point lights only have a position, not a direction. Therefore, we must first calculate the light vector for our point light. To calculate the light vector of a point light, we need to subtract the view space position of the fragment from the position of the point light. We can calculate the view space position of the fragment in our vertex shader. First we need to add another uniform `p3d_ModelViewMatrix` that will receive the model-view matrix:
```glsl
uniform mat4 p3d_ModelViewMatrix;
```

Next we need to add another output attribute `fragPos` that we will assign the fragment position to:
```glsl
out vec3 fragPos;
```

Then we can rewrite our `main` function to calculate the fragment position by multiplying the initial vertex position by the model-view matrix:
```glsl
void main() {
    // Calculate vertex position, fragment position, and surface normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    normal = p3d_NormalMatrix * p3d_Normal;
}
```

Now we need to add an additional input attribute `fragPos` to our fragment shader:
```glsl
in vec3 fragPos;
```

Then we can add a new `calcPointLighting` function like this:
```glsl
vec4 calcPointLighting(int lightIdx, vec3 normal) {
    // Calculate light vector
    vec3 lightVector = p3d_LightSource[lightIdx].position.xyz - fragPos;

    // Calculate attenuation
    float dist = length(lightVector);
    float attenuation = 1 / (p3d_LightSource[lightIdx].constantAttenuation + 
        p3d_LightSource[lightIdx].linearAttenuation * dist + 
        p3d_LightSource[lightIdx].quadraticAttenuation * dist * dist);

    // Normalize light vector
    lightVector = normalize(lightVector);

    // Calculate diffuse lighting
    float nxDir = max(0, dot(normal, lightVector));
    vec4 diffuse = p3d_LightSource[lightIdx].color * nxDir * attenuation;

    // Calculate total lighting
    return (p3d_LightModel.ambient * p3d_Material.ambient + 
        (diffuse * p3d_Material.diffuse));
}
```

The key differences between this function and our `calcDirectionalLighting` function are the formula used to calculate the light vector and the forumula used to calculate attenuation. Attenuation is used to determine how far objects can be from the point light before they are no longer affected by it. The diffuse color is then multiplied by the attenuation value before calculating the total lighting. Now we need to rewrite our `applyLighting` function so it can handle both lights:
```glsl
vec4 applyLighting(vec4 color) {
    // Normalize normal
    vec3 norm = normalize(normal);

    // Calculate lighting
    vec4 lighting = vec4(0);

    for(int i = 0; i < p3d_LightSource.length(); i++) {
        // Calculate directional or point lighting
        if(p3d_LightSource[i].position.w == 0) {
            lighting += calcDirectionalLighting(i, norm);
        } else {
            lighting += calcPointLighting(i, norm);
        }
    }

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}
```

The idea here is that we calculate the sum of the total light from each light source and then multiply the initial color by that value to obtain the final color. If you run your code at this point, you will notice that the sphere is now brighter and has a slight green tint on part of it:  
![all lights](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/04-diffuse_lighting/screenshots/02-multiple_lights.png?raw=true)  

Now that we have fully implemented diffuse lighting, we can proceed to implement specular lighting.
