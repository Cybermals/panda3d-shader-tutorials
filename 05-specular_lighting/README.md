# Lesson 5: Specular Lighting

When light rays strike a surface, part of the light rays get reflected off the surface. In the following diagram, a light ray (V) is reflecting off surface (S). Ray (R) is the reflected light ray, vector (C) is the camera vector, and vector (H) is the half vector. The half vector is halfway in between the angle formed by the light ray (V) and the camera vector (C). We can use the relationship between the half vector (H) and the surface normal (N) to determine how much the surface should be affected by specular lighting:  
![specular lighting](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/05-specular_lighting/diagrams/01-specular_lighting.png?raw=true)

First we need to calculate the camera vector. To do this we will first need to get the camera position. The camera position can be obtained from row 3 of the view matrix, so first we will add the uniform `p3d_ViewMatrix` to our fragment shader:
```glsl
uniform mat4 p3d_ViewMatrix;
```

Next we need to rewrite our `applyLighting` function so it calculates specular lighting:
```glsl
vec4 applyLighting(vec4 color) {
    // Normalize normal and extract camera position from view matrix
    vec3 norm = normalize(normal);
    vec3 cameraPos = p3d_ViewMatrix[3].xyz;

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
        float nxDir = max(0.0, dot(norm, lightVector));
        vec4 diffuse = p3d_LightSource[i].color * nxDir * attenuation;

        // Calculate specular lighting
        vec3 cameraVector = normalize(cameraPos - fragPos);
        vec3 halfVector = normalize(lightVector + cameraVector);
        float nxHalf = max(0.0, dot(norm, halfVector));
        float specularPower = pow(nxHalf, p3d_Material.shininess);
        vec4 specular = p3d_LightSource[i].color * specularPower * 
            attenuation * int(nxDir != 0.0);

        // Calculate total lighting
        lighting += (p3d_LightModel.ambient * p3d_Material.ambient + 
            (diffuse * p3d_Material.diffuse) + 
            (specular * vec4(p3d_Material.specular, 1.0)));
    }

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}
```

To calculate the specular lighting we will need to extract the camera position from the view matrix. After we calculate our diffuse lighting, we will calculate the camera vector, calculate the half vector, calculate the specular power, and calculate the amount of specular lighting. Then we need to add the product of the specular lighting and its corresponding material property to the total lighting.

The procedure here is mostly the same, but we must apply attenuation to the specular color as well before adding it to the total light color. If you run your code at this point, you will see a sphere with both diffuse and specular lighting:  
![full lighting](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/05-specular_lighting/screenshots/01-full_lighting.png?raw=true)  

At this point, we have successuflly implemented all types of lighting on our sphere. Now we just need to add its texture.
