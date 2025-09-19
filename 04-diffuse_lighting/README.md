# Lesson 4: Diffuse Lighting

When light rays strike the surface of an object, part of the light gets absorbed into the surface. We can simulate this by using an algorithm known as Blinn-Phong shading. In the following diagram, we see a light source (L) casting a ray (V) onto a surface (S). We also see a vector (N) perpendicular to the surface (S). Ray (V) is known as the light vector and vector (N) is known as the surface normal:  
![diffuse lighting diagram](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/04-diffuse_lighting/diagrams/01-diffuse_lighting.png?raw=true)

In order to determine how much diffuse lighting from a given light source should affect a surface, we need to calculate the angle (T) between the surface normal (N) and the light vector (V). Let's start by calculating the surface normal in our vertex shader. First we need to add another input attribute `p3d_Normal` that will receive the per-vertex surface normal:
```glsl
in vec3 p3d_Normal;
```

We also need to 2 new uniforms called `p3d_ModelViewMatrix` and `p3d_NormalMatrix` that will receive the modelview and normal matrices:
```glsl
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
```

And we will need 2 new output attributes called `fragPos` and `normal` that will be used to pass the fragment position and transformed normal to the fragment shader:
```glsl
out vec3 fragPos;
out vec3 normal;
```

Now we can rewrite our `main` function like this:
```glsl
void main() {
    // Calculate vertex position, fragment position, and surface normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    normal = p3d_NormalMatrix * p3d_Normal;
}
```

The new lines multiply the vertex position through the modelview matrix to calculate the fragment position and multiply the per-vertex normal through the normal matrix to calculate the transformed normal. Next we need to add `fragPos` and `normal` input attributes to our fragment shader:
```glsl
in vec3 fragPos;
in vec3 normal;
```

However, when passing the normal from our vertex shader to our fragment shader, the interpolation process which occurs between the two shader stages my cause the length of the normal to no longer equal 1. This will throw off our lighting calculations, so we need to normalize the normal by adding the following lines to the beginning of our lighting function:
```glsl
// Normalize normal
vec3 norm = normalize(normal);
```

Next we need to calculate our light vector (V). First we need to add a new uniform `p3d_LightSource` to our fragment shader:
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

The number in square brackets should be equal to the total number of directional, point, and spot lights in the scene. If the `w` component of a light source's `position` member is equal to 0, then it is a directional light. Otherwise, it is a point or spot light. For now, we will only be covering directional and point lights. We can handle both by rewriting our `applyLighting` function like this:
```glsl
vec4 applyLighting(vec4 color) {
    // Normalize normal
    vec3 norm = normalize(normal);

    // Calculate lighting
    vec4 lighting = vec4(0.0);

    for(int i = 0; i < p3d_LightSource.length(); i++) {
        // Calculate light vector
        vec3 lightVector = p3d_LightSource[i].position.xyz - fragPos * 
            p3d_LightSource[i].position.w;

        // Calculate attenuation
        float dist = length(lightVector);
        float attenuation = 1.0 / (p3d_LightSource[i].constantAttenuation + 
            p3d_LightSource[i].linearAttenuation * dist + 
            p3d_LightSource[i].quadraticAttenuation * dist * dist);

        // Normalize light vector
        lightVector = normalize(lightVector);

        // Calculate diffuse lighting
        float nxDir = max(0.0, dot(normal, lightVector));
        vec4 diffuse = p3d_LightSource[i].color * nxDir * attenuation;

        // Calculate total lighting
        lighting += (p3d_LightModel.ambient * p3d_Material.ambient + 
            (diffuse * p3d_Material.diffuse));
    }

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}
```

For the given light and normal, this function will first calculate the light vector by multiplying the fragment position by the W component of the light position and subtracting it from the XYZ portion of the light position. Then it will calculate attenuation based on the length of the light vector. Next it will normalize the light vector. Then the diffuse lighting will be calculated using the dot product of the normal and light vector as well as the light color and attenuation. The ambient and diffuse lighting will then be multiplied by their respective material properties and added to the total light value. Last, the alpha component will be set to the initial alpha and the product of the base color and lighting will be returned.

If you run your code at this point, you should see a blue sphere with diffuse shading:  
![diffuse sphere](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/04-diffuse_lighting/screenshots/01-diffuse_sphere.png?raw=true)

Now that we have fully implemented diffuse lighting, we can proceed to implement specular lighting.
