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


vec4 applyLighting(vec4 color) {
    // Calculate lighting
    vec4 lighting = p3d_LightModel.ambient * p3d_Material.ambient;

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}


void main() {
    // Calculate base color
    vec4 baseColor = vec4(0, .225, .8, 1);

    // Calculate final color
    p3d_FragColor = applyLighting(baseColor);
}
