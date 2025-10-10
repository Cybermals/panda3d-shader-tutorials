#version 140

in vec4 p3d_Vertex;

uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ProjectionMatrix;

out vec3 uv;


void main() {
    // Calculate vertex position
    mat4 skyboxViewMatrix = mat4(mat3(p3d_ViewMatrix));
    gl_Position = p3d_ProjectionMatrix * skyboxViewMatrix * p3d_Vertex;
    gl_Position.z = gl_Position.w;

    // Calculate UV
    uv = p3d_Vertex.xyz;
}
