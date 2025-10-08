#version 140

in vec3 fragPos;
in vec2 uv;
in vec3 toCameraVec;

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

const float PI = 3.14159265359;


float distributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;

    float num = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;
    return num / denom;
}


float geometrySchlickGGX(float NdotV, float roughness) {
    float r = (roughness + 1.0);
    float k = (r * r) / 8.0;

    float num = NdotV;
    float denom = NdotV * (1.0 - k) + k;

    return num / denom;
}


float geometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2 = geometrySchlickGGX(NdotV, roughness);
    float ggx1 = geometrySchlickGGX(NdotL, roughness);

    return ggx1 * ggx2;
}


vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}


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

    vec3 toCamVec = normalize(toCameraVec);
    float refractFactor = dot(toCamVec, vec3(0, 0, 1));
    refractFactor = pow(refractFactor, 20);
    vec4 baseColor = mix(refractColor, reflectColor, refractFactor);

    baseColor = mix(baseColor, vec4(0, .225, .5, 1), .2);
    float metallic = p3d_Material.metallic;
    float emission = 0.0;
    float roughness = p3d_Material.roughness;

    // Fetch normal from normal map and remap it
    vec3 normal = texture(p3d_Texture3, distortedUV).xzy;
    normal = vec3(normal.x * 2 - 1, normal.y, normal.z * 2 - 1);

    // Calculate final color
    p3d_FragColor = applyFog(applyLighting(baseColor, metallic, emission, 
        roughness, normal));
}
