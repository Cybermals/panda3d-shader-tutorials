# Lesson 6: Texture

Now that we have all lighting types implemented, let's add the UV color grid texture to our sphere. The texture is actually already loaded and assigned to the sphere, however we must modify our shaders so that the texture gets applied to the surface of the sphere. The first thing we must do is modify our vertex shader so that it passes the texture coordinates to the fragment shader. We will need an additional input attribute called `p3d_MultiTexCoord0` that will receive the texture coordinate:
```glsl
in vec3 p3d_MultiTexCoord0;
```

Next we will need an additional output called `uv` that will be used to pass the texture coordinate to the fragment shader. Since our texture is 2D, we only need the X and Y components of the texture coordinate in this case:
```glsl
out vec2 uv;
```

Now we can add our texture coordinate calculation to the `main` function:
```glsl
// Calculate UV
uv = p3d_MultiTexCoord0.xy;
```

In our fragment shader, we will need to start by adding a new input attribute `uv`:
```glsl
in vec2 uv;
```

Then we also need to add a new uniform `p3d_Texture0` which will receive the texture to apply to our sphere:
```glsl
uniform sampler2D p3d_Texture0;
```

The only other thing we need to do now is rewrite our `main` function so that it samples the texture and uses the sampled color as the base color for the fragment:
```glsl
void main() {
    // Calculate base color
    vec4 baseColor = texture(p3d_Texture0, uv);

    // Calculate final color
    p3d_FragColor = applyLighting(baseColor);
}
```

If you run your code at this point, you will see a textured sphere with diffuse and specular lighting:
![textured sphere](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/pbr/06-texture/screenshots/01-textured_sphere.png?raw=true)
