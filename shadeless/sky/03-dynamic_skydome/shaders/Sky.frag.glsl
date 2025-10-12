#version 140

in vec2 uv;

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform vec4 horizonColor;
uniform vec4 zenithColor;
uniform vec2 cloudScrollVec;
uniform vec2 cloudScale;
uniform vec2 celestialScrollVec;
uniform float osg_FrameTime;

out vec4 p3d_FragColor;


void main() {
    // Calculate base color
    vec4 baseColor = horizonColor;
    vec4 colorMask = texture(p3d_Texture0, uv);
    vec4 cloudColor = texture(p3d_Texture1, uv / cloudScale + cloudScrollVec * osg_FrameTime);
    vec4 celestialColor = texture(p3d_Texture2, uv / vec2(2, 1) + celestialScrollVec * osg_FrameTime);
    baseColor = mix(baseColor, zenithColor, colorMask.r);
    baseColor = mix(baseColor, celestialColor, celestialColor.a);
    baseColor = mix(baseColor, cloudColor, cloudColor.a);

    // Calculate final color
    p3d_FragColor = baseColor;
}
