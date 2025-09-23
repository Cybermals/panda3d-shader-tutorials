# Lesson 7: MER Map

Thus far we have been using constant metallic, emission, and roughness values for the entire sphere. However, there are times when you may want different parts of a mesh to have different material properties. For example, our sphere could be metallic and smooth but the letters and numbers on it could be dialectic and rough. We can achieve this by using something known as an MER map. An MER map is a texture where red represents metallic, green represents emission, and blue represents roughness. For this lesson, we will need to use a different sphere mesh which includes an MER map. We can use the fancy sphere mesh included in the mesh archive that you previously downloaded and unzipped. In `main.py`, change the part where you load the sphere mesh like this:
```python
# Load sphere mesh
self.sphere = self.loader.load_model("meshes/FancySphere.gltf")
self.sphere.set_pos(0, 5, 0)
self.sphere.set_shader(self.sphere_shader)
self.sphere.reparent_to(self.render)
```
 
We will also need to add a uniform for the MER map to our fragment shader:
```glsl
uniform sampler2D p3d_Texture1;
```

Then modify your lighting function like this:
```glsl
vec4 applyLighting(vec4 albedo, float metallic, float emission, 
    float roughness) {
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
        Lo += p3d_Material.emission.rgb;
    }

    // Apply lighting to initial color
    vec3 ambient = p3d_LightModel.ambient.rgb * albedo.rgb;
    vec3 color = ambient + Lo;
    color = color / (color + vec3(1.0));
    return vec4(color, albedo.a);
}
```

And rewrite your main function like this:
```glsl
void main() {
    // Calculate base color, metallic, emission, and roughness
    vec4 baseColor = texture(p3d_Texture0, uv);
    vec4 mer = texture(p3d_Texture1, uv);
    float metallic = mer.r;
    float emission = mer.g;
    float roughness = mer.b;

    // Calculate final color
    p3d_FragColor = applyFog(applyLighting(baseColor, metallic, emission, 
        roughness));
}
```

Making these changes will cause the fragment shader to obtain the metallic, emission, and roughness values from the MER map. If you run your code at this point you should see this:
![mer map](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/07-mer_map/screenshots/01-mer_map.png?raw=true)
