# Lesson 4: Diffuse Lighting

When light rays strike the surface of an object, part of the light gets absorbed into the surface. We can simulate this by using an algorithm known as Blinn-Phong shading. In the following diagram, we see a light source (L) casting a ray (V) onto a surface (S). We also see a vector perpendicular to the surface (N). Ray (V) is known as the light vector and vector (N) is known as the surface normal:  
diffuse lighting diagram

In order to determine how much diffuse lighting from a given light source should affect a surface, we need to calculate the angle (T) between the surface normal (N) and the light vector (V). Let's start by calculating the surface normal in our vertex shader. First we need to add another input attribute `p3d_Normal` that will receive the per-vertex surface normal:
```glsl
in vec3 p3d_Normal;
```

We also need to add another uniform `p3d_NormalMatrix` that will receive the normal matrix:
```glsl
uniform mat3 p3d_NormalMatrix;
```

And we will need a new output attribute `normal` that will be used to pass the transformed normal to the fragment shader:
```glsl
out vec3 normal;
```

Now we can rewrite our `main` function like this:
```glsl
void main() {
    // Calculate vertex position and surface normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    normal = p3d_NormalMatrix * p3d_Normal;
}
```

The new line multiplies the per-vertex normal through the normal matrix and assigns it to the `normal` output attribute that will be passed to the fragment shader. Next we need to add a `normal` input attribute to our fragment shader:
```glsl
in vec3 normal;
```
