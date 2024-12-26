# Lesson 7: Normal Mapping

So far, you may have noticed that the lighting for our water isn't very impressive. This is because we didn't define any normals for our geometry. One way to fix this issue would be to simply change our vertex format to include normals and provide a normal for each vertex. However, water is not perfectly flat. Therefore, what we really need to do is define a normal for each fragment rather than each vertex. To do this we will use a normal map. In a normal map, the color channels are used to encode surface normals which we can then use in our fragment shader. For this lesson, I have provided a normal map in the image archive we previously unpacked. However, we will need to modify our shaders in order to use the normal map. Let's start by removing the `normal` input attribute from our fragment shader since we will be obtaining the surface normals from the normal map. And then we will need to add a new uniform for our normal map:
```glsl
uniform sampler2D p3d_Texture3;
```

Afterwards, we will rewrite our `applyLighting` function like this:
```glsl
vec4 applyLighting(vec4 color, vec2 distortedUV) {
    // Fetch normal from normal map and remap it
    vec3 normal = texture(p3d_Texture3, distortedUV).xzy;
    normal = vec3(normal.x * 2 - 1, normal.y, normal.z * 2 - 1);

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

We will also need to modify the last part of our `main` function like this:
```glsl
// Calculate final color
p3d_FragColor = applyFog(applyLighting(baseColor, distortedUV));
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
![normal mapping](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/07-normal_mapping/screenshots/01-normal_mapping.png?raw=true)
