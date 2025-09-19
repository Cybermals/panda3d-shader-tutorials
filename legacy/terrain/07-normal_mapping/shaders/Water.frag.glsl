#version 140

in vec3 fragPos;
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
uniform vec2 winSize;
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;
uniform float osg_FrameTime;
uniform float waveSpeed;

out vec4 p3d_FragColor;


vec4 applyLighting(vec4 color, vec2 distortedUV) {
    // Fetch normal from normal map and remap it
    vec3 normal = texture(p3d_Texture3, distortedUV).xzy;
    normal = vec3(normal.x * 2 - 1, normal.y, normal.z * 2 - 1);

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
    // Calculate refraction and reflection UV coordinates
    vec2 texSize = textureSize(p3d_Texture0, 0).xy;
    vec2 texelSize = 1 / texSize;
    vec2 ndc = gl_FragCoord.xy * texelSize;
    vec2 refractUV = vec2(ndc.x, ndc.y);
    vec2 reflectUV = vec2(-((texSize.x - winSize.x) * texelSize.x + ndc.x), ndc.y);

    // Apply distortion
    vec2 distortedUV = texture(p3d_Texture2, vec2(uv.x + osg_FrameTime * waveSpeed, uv.y)).rg * .1;
    distortedUV = uv + vec2(distortedUV.x, distortedUV.y + osg_FrameTime * waveSpeed);
    vec2 totalDistortion = (texture(p3d_Texture2, distortedUV).rg * 2 - 1) * .02;
    
    refractUV += totalDistortion;
    refractUV = clamp(refractUV, .001, .999);

    reflectUV += totalDistortion;
    reflectUV.x = clamp(reflectUV.x, -.999, -.001);
    reflectUV.y = clamp(reflectUV.y, .001, .999);

    // Calculate base color
    vec4 refractColor = texture(p3d_Texture0, refractUV);
    vec4 reflectColor = texture(p3d_Texture1, reflectUV);

    vec4 baseColor = mix(refractColor, reflectColor, .5);

    baseColor = mix(baseColor, vec4(0, .225, .5, 1), .2);

    // Calculate final color
    p3d_FragColor = applyFog(applyLighting(baseColor, distortedUV));
}
