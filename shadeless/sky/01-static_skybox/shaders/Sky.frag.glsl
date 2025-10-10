#version 140

in vec3 uv;

uniform samplerCube p3d_Texture0;

out vec4 p3d_FragColor;


void main() {
    // Calculate final color
    p3d_FragColor = texture(p3d_Texture0, uv);
}
