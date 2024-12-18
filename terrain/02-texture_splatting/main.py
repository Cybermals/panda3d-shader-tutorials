from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    SamplerState,
    Shader,
    Vec4
)


# Application Class
# =================
class TerrainDemo(ShowBase):
    def __init__(self):
        # Call base constructor
        ShowBase.__init__(self)

        # Enable auto shaders
        self.render.set_shader_auto()

        # Setup lighting
        self.ambient_light = self.render.attach_new_node(AmbientLight("AmbientLight"))
        self.ambient_light.node().set_color(Vec4(.2, .2, .2, 1))
        self.render.set_light(self.ambient_light)

        self.sun = self.render.attach_new_node(DirectionalLight("Sun"))
        self.sun.set_hpr(45, -45, 0)
        self.render.set_light(self.sun)

        # Load shaders
        self.terrain_shader = Shader.load(
            Shader.SL_GLSL,
            "shaders/Terrain.vert.glsl",
            "shaders/Terrain.frag.glsl"
        )

        # Load textures
        self.grass_tex = self.loader.load_texture("images/Grass.png")
        self.grass_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.grass_tex.magfilter = SamplerState.FT_linear_mipmap_linear

        # Load terrain
        self.terrain = self.loader.load_model("meshes/Terrain")
        self.terrain.set_scale(256, 256, 256)
        self.terrain.set_pos(0, 261, 0)

        self.terrain.set_shader(self.terrain_shader)

        self.terrain.set_texture(self.grass_tex)

        self.terrain.reparent_to(self.render)


# Entry Point
# ===========
if __name__ == "__main__":
    TerrainDemo().run()
