# Lesson 8: Fresnel

Our water is looking great so far, however there is still something missing. If you move the camera around, you will notice that the water looks the same regardless of the viewing angle. But realistic water reflects more when the camera is more parallel to the water and it reflects less when the camera is more perpendicular to the water. To achieve this effect, we will need to use something known as the fresnel effect. Let's start by adding a new uniform to our vertex shader:
```glsl
uniform mat4 p3d_ViewMatrix;
```

We also need to add a new output attribute:
```glsl
out vec3 toCameraVec;
```

Then we will calculate the vector from the water to the camera in our `main` function like this:
```glsl
// Calculate vector to camera
vec3 camPos = p3d_ViewMatrix[3].xyz;
toCameraVec = fragPos - camPos;
toCameraVec.x = 0;
```

You may be wondering why I set the x component to 0 in this part of the code. The reason why I do this is to prevent a weird bug that occurs when calculating the fresnel value in view space. Next we will add a new input attribute to our fragment shader:
```glsl
in vec3 toCameraVec;
```

And we will rewrite the portion of our `main` method where we calculate the base color like this:
```glsl
// Calculate base color
vec4 refractColor = texture(p3d_Texture0, refractUV);
vec4 reflectColor = texture(p3d_Texture1, reflectUV);

vec3 toCamVec = normalize(toCameraVec);
float refractFactor = dot(toCamVec, vec3(0, 0, 1));
refractFactor = pow(refractFactor, 20);
vec4 baseColor = mix(refractColor, reflectColor, refractFactor);

baseColor = mix(baseColor, vec4(0, .225, .5, 1), .2);
```

Notice that now we are using the refract factor instead of mixing the reflection and refraction colors equally. And If you look down at the water from a more perpendicular angle, you will see less reflections:  
![fresnel](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/legacy/terrain/08-fresnel/screenshots/01-fresnel.png?raw=true)
