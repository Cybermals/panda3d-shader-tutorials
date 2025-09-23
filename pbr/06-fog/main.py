from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Fog,
    load_prc_file,
    PointLight,
    Shader,
    Vec3,
    Vec4
)


# Application Class
# =================
class ShaderDemo(ShowBase):
    def __init__(self):
        # Load config file
        load_prc_file("settings.prc")
        
        # Call the base constructor
        ShowBase.__init__(self)

        # Load custom shaders
        self.sphere_shader = Shader.load(
            Shader.SL_GLSL,
            "shaders/Sphere.vert.glsl",
            "shaders/Sphere.frag.glsl"
        )

        # Setup lighting
        self.ambient_light = self.render.attach_new_node(AmbientLight("AmbientLight"))
        self.ambient_light.node().set_color(Vec4(.2, .2, .2, 1))
        self.render.set_light(self.ambient_light)

        self.sun = self.render.attach_new_node(DirectionalLight("Sun"))
        self.sun.set_hpr(45, -45, 0)
        self.render.set_light(self.sun)

        self.green_light = self.render.attach_new_node(PointLight("GreenLight"))
        self.green_light.node().set_color(Vec4(0, 1, 0, 1))
        self.green_light.node().set_attenuation(Vec3(1, .1, .5))
        self.green_light.set_pos(0, 3, 0)
        self.render.set_light(self.green_light)

        # Setup fog
        self.fog = Fog("Fog")
        self.fog.set_color(1, 1, 1)
        self.render.set_fog(self.fog)

        # Load sphere mesh
        self.sphere = self.loader.load_model("meshes/Sphere.gltf")
        self.sphere.set_pos(0, 5, 0)
        self.sphere.set_shader(self.sphere_shader)
        self.sphere.reparent_to(self.render)


# Entry Point
# ===========
if __name__ == "__main__":
    ShaderDemo().run()
