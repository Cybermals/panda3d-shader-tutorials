from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    SamplerState,
    Shader,
    TextureStage,
    Vec2,
    Vec3,
    Vec4
)

from water import WaterPlane


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

        self.dirt_tex = self.loader.load_texture("images/Dirt.png")
        self.dirt_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.dirt_tex.magfilter = SamplerState.FT_linear_mipmap_linear

        self.rock_tex = self.loader.load_texture("images/Rock.png")
        self.rock_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.rock_tex.magfilter = SamplerState.FT_linear_mipmap_linear

        self.blank_tex = self.loader.load_texture("images/Blank.png")
        self.blank_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.blank_tex.magfilter = SamplerState.FT_linear_mipmap_linear

        self.color_mask_tex = self.loader.load_texture("images/ColorMask.png")
        self.color_mask_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.color_mask_tex.magfilter = SamplerState.FT_linear_mipmap_linear

        # Load terrain
        self.terrain = self.loader.load_model("meshes/Terrain")
        self.terrain.set_scale(256, 256, 256)
        self.terrain.set_pos(0, 261, 0)

        self.terrain.set_shader(self.terrain_shader)
        self.terrain.set_shader_input("texScale0", Vec2(.1, .1))
        self.terrain.set_shader_input("texScale1", Vec2(.1, .1))
        self.terrain.set_shader_input("texScale2", Vec2(.1, .1))
        self.terrain.set_shader_input("texScale3", Vec2(.1, .1))

        stage1 = TextureStage("Dirt")
        stage2 = TextureStage("Rock")
        stage3 = TextureStage("Blank")
        stage4 = TextureStage("ColorMask")

        self.terrain.set_texture(self.grass_tex)
        self.terrain.set_texture(stage1, self.dirt_tex)
        self.terrain.set_texture(stage2, self.rock_tex)
        self.terrain.set_texture(stage3, self.blank_tex)
        self.terrain.set_texture(stage4, self.color_mask_tex)

        self.terrain.reparent_to(self.render)

        # Load water plane
        self.water = WaterPlane(
            Vec3(0, 261, -20),
            scale=Vec3(256, 256, 1)
        )


# Entry Point
# ===========
if __name__ == "__main__":
    TerrainDemo().run()
