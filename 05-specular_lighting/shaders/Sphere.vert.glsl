#version 140

in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

out vec3 fragPos;
out vec3 normal;


void main() {
    // Calculate vertex position, fragment position, and surface normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    normal = p3d_NormalMatrix * p3d_Normal;
}
