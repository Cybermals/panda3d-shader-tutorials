#version 140

in vec2 uv;

uniform sampler2D p3d_Texture0;

out vec4 p3d_FragColor;


void main() {
    // Calculate final color
    p3d_FragColor = texture(p3d_Texture0, uv);
}
