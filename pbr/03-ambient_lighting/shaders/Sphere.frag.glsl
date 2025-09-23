#version 140

uniform struct p3d_LightModelParameters {
    vec4 ambient;
} p3d_LightModel;
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

out vec4 p3d_FragColor;


vec4 applyLighting(vec4 albedo) {
    // Apply lighting to initial color
    vec3 ambient = p3d_LightModel.ambient.rgb * albedo.rgb;
    vec3 color = ambient;
    color = color / (color + vec3(1.0));
    return vec4(pow(color, vec3(1.0 / 2.2)), albedo.a);
}


vec4 srgbToLinear(vec4 color) {
    return vec4(pow(color.rgb, vec3(2.2)), color.a);
}


void main() {
    // Calculate base color
    vec4 baseColor = vec4(0.0, .225, .8, 1.0);
    baseColor = srgbToLinear(baseColor);

    // Calculate final color
    p3d_FragColor = applyLighting(baseColor);
}
