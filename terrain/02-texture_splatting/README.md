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
texture zip file

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
