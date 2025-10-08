# Lesson 7: Normal Mapping

So far, you may have noticed that the lighting for our water isn't very impressive. This is because we didn't define any normals for our geometry. One way to fix this issue would be to simply change our vertex format to include normals and provide a normal for each vertex. However, water is not perfectly flat. Therefore, what we really need to do is define a normal for each fragment rather than each vertex. To do this we will use a normal map. In a normal map, the color channels are used to encode surface normals which we can then use in our fragment shader. For this lesson, I have provided a normal map in the image archive we previously unpacked. However, we will need to modify our shaders in order to use the normal map. Let's start by removing the `normal` input attribute from our fragment shader since we will be obtaining the surface normals from the normal map. And then we will need to add a new uniform for our normal map:
```glsl
uniform sampler2D p3d_Texture3;
```

Afterwards, we will rewrite our `applyLighting` function like this:
```glsl
vec4 applyLighting(vec4 albedo, float metallic, float emission, 
    float roughness, vec3 normal) {
    // Normalize normal and extract camera position from view matrix
    vec3 N = normalize(normal);
    vec3 cameraPos = p3d_ViewMatrix[3].xyz;

    // Calculate view vector
    vec3 V = normalize(cameraPos - fragPos);

    // Calculate base reflectivity
    vec3 F0 = vec3(.04);
    F0 = mix(F0, albedo.rgb, metallic);

    // Calculate total radiance
    vec3 Lo = vec3(0.0);

    for(int i = 0; i < p3d_LightSource.length(); i++) {
        // Calculate per-light radiance
        vec3 lightDir = p3d_LightSource[i].position.xyz - fragPos * 
            p3d_LightSource[i].position.w;
        vec3 L = normalize(lightDir);
        vec3 H = normalize(V + L);
        float dist = length(lightDir);
        vec3 atten = p3d_LightSource[i].attenuation;
        float attenuation = 1.0 / (atten.x + atten.y * dist + 
            atten.z * dist * dist);
        vec3 radiance = p3d_LightSource[i].color.rgb * attenuation;

        // Cook-Torrance BRDF
        float NDF = distributionGGX(N, H, roughness);
        float G = geometrySmith(N, V, L, roughness);
        vec3 F = fresnelSchlick(max(dot(H, V), 0.0), F0);

        vec3 kS = F;
        vec3 kD = vec3(1.0) - kS;
        kD *= 1.0 - metallic;

        vec3 num = NDF * G * F;
        float denom = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 
            .0001;
        vec3 specular = num / denom;

        // Add to outgoing radiance Lo
        float NdotL = max(dot(N, L), 0.0);
        Lo += (kD * albedo.rgb / PI + specular) * radiance * NdotL;

        // Add emission
        Lo += p3d_Material.emission.rgb * emission;
    }

    // Apply lighting to initial color
    vec3 ambient = p3d_LightModel.ambient.rgb * albedo.rgb * 
        p3d_Material.refractiveIndex;
    vec3 color = ambient + Lo;
    color = color / (color + vec3(1.0));
    return vec4(color, albedo.a);
}
```

We will also need to modify the last part of our `main` function like this:
```glsl
// Calculate final color
// Fetch normal from normal map and remap it
vec3 normal = texture(p3d_Texture3, distortedUV).xzy;
normal = vec3(normal.x * 2 - 1, normal.y, normal.z * 2 - 1);

// Calculate final color
p3d_FragColor = applyFog(applyLighting(baseColor, metallic, emission, 
    roughness, normal));
```

Then we need to remove the `p3d_NormalMatrix` uniform and `normal` output attribute from our vertex shader. We also need to rewrite our `main` function like this:
```glsl
void main() {
    // Calculate position and fragment position
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);

    // Calculate UV
    uv = vec2(p3d_Vertex.x / 2 + .5, p3d_Vertex.y / 2 + .5);

    // Calculate clip distance
    gl_ClipDistance[0] = dot(vec4(fragPos, 1), p3d_ClipPlane[0]);
}
```

We also need to go to the constructor for our `WaterPlane` class and load our normal map like this:
```python
self.normal_map_tex = base.loader.load_texture("images/WaterNormal.png")
self.normal_map_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.normal_map_tex.magfilter = SamplerState.FT_linear_mipmap_linear
```

And we need to add a texture stage for our normal map:
```python
stage1 = TextureStage("ReflectionTex")
stage2 = TextureStage("DUDVMap")
stage3 = TextureStage("NormalMap")

self.plane.set_texture(self.refract_tex)
self.plane.set_texture(stage1, self.reflect_tex)
self.plane.set_texture(stage2, self.dudv_map_tex)
self.plane.set_texture(stage3, self.normal_map_tex)
```

If we run our code now, the lighting on the surface of the water should be better:  
![normal mapping](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/terrain/07-normal_mapping/screenshots/01-normal_mapping.png?raw=true)
