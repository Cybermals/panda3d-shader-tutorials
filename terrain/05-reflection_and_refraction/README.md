# Lesson 5: Reflection and Refraction

In this lesson, I will show you how to add reflection and refraction to our water plane. In order to do this, we will need to render the scene to 2 textures. Let's start by discussing how this will work. When looking at the water, objects below the water will get refracted on the surface of the water:  
![refraction diagram](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/diagrams/01-refraction.png?raw=true)

And objects above the water will get reflected on the surface of the water:  
![reflection diagram](https://github.com/Cybermals/panda3d-shader-tutorials/blob/main/terrain/05-reflection_and_refraction/diagrams/02-reflection.png?raw=true)

We can create a refraction texture by rendering the scene from the viewpoint of the main camera, however we must use a slightly different approach for rendering the reflection texture. In order to capture the objects above the water, we will need to render the scene from a camera below the water and looking up as depicted in this diagram:
reflection camera
