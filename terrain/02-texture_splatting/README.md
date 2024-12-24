# Lesson 2: Texture Splatting

In order to use multiple textures on our terrain, we can utilize a technique known as texture splatting. Let's start by copying the shaders we made in my previous tutorial series. We will be naming them `Terrain.vert.glsl` and `Terrain.frag.glsl` and placing them in a folder called `shaders` within your project folder this time. For convenience, I will post the code for both below.  

`Terrain.vert.glsl`:
```glsl
#version 140

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec3 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

out vec3 fragPos;
out vec3 normal;
out vec2 uv;


void main() {
    // Calculate vertex position, fragment position, and surface normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    normal = p3d_NormalMatrix * p3d_Normal;

    // Calculate UV
    uv = p3d_MultiTexCoord0.xy;
}
```
  
`Terrain.frag.glsl`:
```glsl
#version 140

in vec3 fragPos;
in vec3 normal;
in vec2 uv;

uniform mat4 p3d_ViewMatrix;
uniform struct p3d_LightModelParameters {
    vec4 ambient;
} p3d_LightModel;
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
uniform struct p3d_FogParameters {
    vec4 color;
    float density;
    float start;
    float end;
    float scale; // 1.0 / (end - start)
} p3d_Fog;
uniform sampler2D p3d_Texture0;

out vec4 p3d_FragColor;


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


vec4 applyFog(vec4 color) {
    // If fog is disabled, skip fog calculations
    if(p3d_Fog.start == p3d_Fog.end) {
        return color;
    }

    // Calculate linear fog
    float dist = length(fragPos);
    float fogFactor = (p3d_Fog.end - dist) / (p3d_Fog.end - p3d_Fog.start);
    fogFactor = clamp(fogFactor, 0, 1);
    return mix(p3d_Fog.color, color, fogFactor);
}


void main() {
    // Calculate base color
    vec4 baseColor = texture(p3d_Texture0, uv);

    // Calculate final color
    p3d_FragColor = applyFog(applyLighting(baseColor));
}
```

Now your folder heirarchy should look like this:
```
project/
    meshes/
        Terrain.egg
        Water.egg
    shaders/
        Terrain.frag.glsl
        Terrain.vert.glsl
    main.py
```

Next we need to load our shaders. Modify your imports like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Shader,
    Vec4
)
```

Add the following code before the part where you load your terrain:
```python
# Load shaders
self.terrain_shader = Shader.load(
    Shader.SL_GLSL,
    "shaders/Terrain.vert.glsl",
    "shaders/Terrain.frag.glsl"
)
```

Then add the following code where you load your terrain:
```python
self.terrain.set_shader(self.terrain_shader)
```

If you run your code at this point, you won't see any differences because we haven't yet loaded any textures for our terrain. For this tutorial series, we will be using some simple terrain textures I made. Download the zip file from the following URL:
https://github.com/Cybermals/panda3d-shader-tutorials/raw/refs/heads/main/terrain/images.zip

Now extract the zip file so your folder structure looks like this:
```
project/
    images/
        Blank.png
        ColorMask.png
        Dirt.png
        Grass.png
        Heightmap.png
        Heightmap2.png
        Rock.png
        WaterDUDV.png
        WaterNormal.png
    meshes/
        Terrain.egg
        Water.egg
    shaders/
        Terrain.frag.glsl
        Terrain.vert.glsl
    main.py
```

Let's start by just loading the grass texture. Modify your imports like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    SamplerState,
    Shader,
    Vec4
)
```

Add the following code before the part where you load your terrain mesh:
```python
# Load textures
self.grass_tex = self.loader.load_texture("images/Grass.png")
self.grass_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.grass_tex.magfilter = SamplerState.FT_linear_mipmap_linear
```

This will load the grass texture and turn on the linear mipmap filter for this texture. Now we can set this texture on our terrain by adding the following code after where we set the shader for our terrain:
```python
self.terrain.set_texture(self.grass_tex)
```

If you run your code at this point, you will see a texture on the terrain like this:  
![basic texture](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/02-texture_splatting/screenshots/01-basic_texture.png?raw=true)

However, the resolution of the texture is low due to the way it is being stretched to fit the terrain. Let's fix this by scaling the texture in our shader. And let's also make it so we can set the scale via a shader input. First, we need to add a new uniform `texScale0` to our fragment shader:
```glsl
uniform vec2 texScale0;
```

And we also need to divide our UV coordinate by the scale before sampling the texture:
```glsl
// Calculate base color
vec4 baseColor = texture(p3d_Texture0, uv / texScale0);
```

We also need to pass the scale into our shader. First modify your imports like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    SamplerState,
    Shader,
    Vec2,
    Vec4
)
```

Then add this code below where you set the shader for the terrain:
```python
self.terrain.set_shader_input("texScale0", Vec2(.1, .1))
```

If you run your code at this point, you will see that the resolution of the texture on the terrain has improved:  
![texture scaling](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/02-texture_splatting/screenshots/02-texture_scaling.png?raw=true)

However, we are still only using one texture on our terrain. Let's try loading some more textures next:
```python
# Load textures
self.grass_tex = self.loader.load_texture("images/Grass.png")
self.grass_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.grass_tex.magfilter = SamplerState.FT_linear_mipmap_linear

self.dirt_tex = self.loader.load_texture("images/Dirt.png")
self.dirt_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.dirt_tex.magfilter = SamplerState.FT_linear_mipmap_linear

self.rock_tex = self.loader.load_texture("images/Rock.png")
self.rock_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.rock_tex.magfilter = SamplerState.FT_linear_mipmap_linear

self.blank_tex = self.loader.load_texture("images/Blank.png")
self.blank_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.blank_tex.magfilter = SamplerState.FT_linear_mipmap_linear
```

We have a total of 4 textures loaded now, but how can we use them all on our terrain? If we call `set_texture` repeatedly, we will just be changing the first texture used on the terrain. However, it is possible to assign multiple textures at once by assigning each texture to a different texture stage. First we need to modify our imports like this:
```python
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    SamplerState,
    Shader,
    TextureStage,
    Vec2,
    Vec4
)
```

Now we can create a texture stage for each additional texture we want to use and assign a different texture to each:
```python
stage1 = TextureStage("Dirt")
stage2 = TextureStage("Rock")
stage3 = TextureStage("Blank")

self.terrain.set_texture(self.grass_tex)
self.terrain.set_texture(stage1, self.dirt_tex)
self.terrain.set_texture(stage2, self.rock_tex)
self.terrain.set_texture(stage3, self.blank_tex)
```

We will also need to add more uniforms to our fragment shader that will receive the additional textures:
```glsl
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;
```

And we need to add scale uniforms for the additional textures as well:
```glsl
uniform vec2 texScale0;
uniform vec2 texScale1;
uniform vec2 texScale2;
uniform vec2 texScale3;
```

The new scale uniforms will need to be populated like our first one:
```python
self.terrain.set_shader(self.terrain_shader)
self.terrain.set_shader_input("texScale0", Vec2(.1, .1))
self.terrain.set_shader_input("texScale1", Vec2(.1, .1))
self.terrain.set_shader_input("texScale2", Vec2(.1, .1))
self.terrain.set_shader_input("texScale3", Vec2(.1, .1))
```

However, there is still something that is missing. We have not defined a way to determine which texture should be used for each part of the terrain. To do this, we will need to use an additional texture called a color mask. Let's start by loading it:
```python
self.color_mask_tex = self.loader.load_texture("images/ColorMask.png")
self.color_mask_tex.minfilter = SamplerState.FT_linear_mipmap_linear
self.color_mask_tex.magfilter = SamplerState.FT_linear_mipmap_linear
```

We also need to add an additional texture stage for it:
```python
stage1 = TextureStage("Dirt")
stage2 = TextureStage("Rock")
stage3 = TextureStage("Blank")
stage4 = TextureStage("ColorMask")

self.terrain.set_texture(self.grass_tex)
self.terrain.set_texture(stage1, self.dirt_tex)
self.terrain.set_texture(stage2, self.rock_tex)
self.terrain.set_texture(stage3, self.blank_tex)
self.terrain.set_texture(stage4, self.color_mask_tex)
```

And in our fragment shader, we will need to add another uniform for this texture:
```glsl
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;
uniform sampler2D p3d_Texture4;
```

Now we need to sample the first 4 textures like this:
```glsl
// Calculate base color
vec4 baseColor = texture(p3d_Texture0, uv / texScale0);
vec4 layer1 = texture(p3d_Texture1, uv / texScale1);
vec4 layer2 = texture(p3d_Texture2, uv / texScale2);
vec4 layer3 = texture(p3d_Texture3, uv / texScale3);
```

Once we have sampled those textures, we will sample the mask as well. However, we will not be scaling the mask:
```glsl
vec4 mask0 = texture(p3d_Texture4, uv);
```

And now we can use each color channel of the mask to determine how to blend the other 4 textures:
```glsl
baseColor = mix(baseColor, layer1, mask0.r);
baseColor = mix(baseColor, layer2, mask0.g);
baseColor = mix(baseColor, layer3, mask0.b);
```

The idea is that black represents the base texture. In this case our base texure is grass. Red represents the layer 1 texure which is dirt in this case. Green represents the layer 2 texture which is rock in this case. And blue represents the layer 3 texture which is blank in this case. If you run your code now, you will see that the terrain now has grass, dirt, and rock:  
![texture splatting](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/02-texture_splatting/screenshots/03-texture_splatting.png?raw=true)

If you need more textures, you can add 3 more textures and another mask. Each additional mask lets you use 3 more textures.
