#version 140

in vec4 p3d_Vertex;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ViewMatrix;
uniform vec4 p3d_ClipPlane[1];

out vec3 fragPos;
out vec2 uv;
out vec3 toCameraVec;


void main() {
    // Calculate position and fragment position
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);

    // Calculate UV
    uv = vec2(p3d_Vertex.x / 2 + .5, p3d_Vertex.y / 2 + .5);

    // Calculate clip distance
    gl_ClipDistance[0] = dot(vec4(fragPos, 1), p3d_ClipPlane[0]);

    // Calculate vector to camera
    vec3 camPos = p3d_ViewMatrix[3].xyz;
    toCameraVec = fragPos - camPos;
    toCameraVec.x = 0;
}