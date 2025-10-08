#version 140

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec3 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
uniform vec4 p3d_ClipPlane[1];

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

    // Calculate clip distance
    gl_ClipDistance[0] = dot(vec4(fragPos, 1), p3d_ClipPlane[0]);
}
