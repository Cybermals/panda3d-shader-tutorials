# Lesson 5: Specular Lighting

When light rays strike a surface, part of the light rays get reflected off the surface. In the following diagram, a light ray (V) is reflecting off surface (S). Ray (R) is the reflected light ray, vector (C) is the camera vector, and vector (H) is the half vector. The half vector is halfway in between the angle formed by the light ray (V) and the camera vector (C). We can use the relationship between the half vector (H) and the surface normal (N) to determine how much the surface should be affected by specular lighting:  
specular lighting

First we need to calculate the camera vector. To do this we will first need to get the camera position. The camera position can be obtained from row 3 of the view matrix, so first we will add the uniform `p3d_ViewMatrix` to our fragment shader:
```glsl
uniform mat4 p3d_ViewMatrix;
```

Next we need to rewrite our `applyLighting` function so it extracts the camera position from the view matrix and passes it as a parameter to either light calculation function:
```glsl
vec4 applyLighting(vec4 color) {
    // Normalize normal and extract camera position from view matrix
    vec3 norm = normalize(normal);
    vec3 cameraPos = p3d_ViewMatrix[3].xyz;

    // Calculate lighting
    vec4 lighting = vec4(0);

    for(int i = 0; i < p3d_LightSource.length(); i++) {
        // Calculate directional or point lighting
        if(p3d_LightSource[i].position.w == 0) {
            lighting += calcDirectionalLighting(i, norm, cameraPos);
        } else {
            lighting += calcPointLighting(i, norm, cameraPos);
        }
    }

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}
```

Next we need to rewrite our `calcDirectionalLight` function so it calculates specular lighting:
```glsl
vec4 calcDirectionalLighting(int lightIdx, vec3 normal, vec3 cameraPos) {
    // Calculate light vector
    vec3 lightVector = normalize(p3d_LightSource[lightIdx].position.xyz);

    // Calculate diffuse lighting
    float nxDir = max(0, dot(normal, lightVector));
    vec4 diffuse = p3d_LightSource[lightIdx].color * nxDir;

    // Calculate specular lighting
    vec4 specular = vec4(0);

    if(nxDir != 0) {
        vec3 cameraVector = normalize(cameraPos - fragPos);
        vec3 halfVector = normalize(lightVector + cameraVector);
        float nxHalf = max(0, dot(normal, halfVector));
        float specularPower = pow(nxHalf, p3d_Material.shininess);
        specular = p3d_LightSource[lightIdx].color * specularPower;
    }

    // Calculate total lighting
    return (p3d_LightModel.ambient * p3d_Material.ambient + 
        (diffuse * p3d_Material.diffuse) + 
        (specular * vec4(p3d_Material.specular, 1)));
}
```

To calculate specular lighting, we will first set the specular color to black. If the diffuse factor is not 0, then we will calculate the camera vector by subtracting the fragment position from the camera position and normalizing the result. Then we will calculate the sum of the light vector and camera vector and normalize the result to get the half vector. We can then calculate the specular factor as the dot product of the per-vertex normal and half vector. The specular factor should never be less than 0, so we need to use the `max` function to enforce that. Next we will raise the specular factor to the power indicated by the material `shininess` property to get the specular power value. we then multiply the light color by the specular power to get the specular color. And we also need to add the product of the specular color and the material `specular` property to the total light color.  

We will also need to rewrite our `calcPointLighting` function so it calculates specular lighting as well:
```glsl
vec4 calcPointLighting(int lightIdx, vec3 normal, vec3 cameraPos) {
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

    // Calculate specular lighting
    vec4 specular = vec4(0);

    if(nxDir != 0) {
        vec3 cameraVector = normalize(cameraPos - fragPos);
        vec3 halfVector = normalize(lightVector + cameraVector);
        float nxHalf = max(0, dot(normal, halfVector));
        float specularPower = pow(nxHalf, p3d_Material.shininess);
        specular = p3d_LightSource[lightIdx].color * specularPower * attenuation;
    }

    // Calculate total lighting
    return (p3d_LightModel.ambient * p3d_Material.ambient + 
        (diffuse * p3d_Material.diffuse) + 
        (specular * vec4(p3d_Material.specular, 1)));
}
```

The procedure here is mostly the same, but we must apply attenuation to the specular color as well before adding it to the total light color. If you run your code at this point, you will see a sphere with both diffuse and specular lighting:
full lighting
