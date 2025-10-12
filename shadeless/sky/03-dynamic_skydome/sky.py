from panda3d.core import (
    DepthTestAttrib,
    OmniBoundingVolume,
    Shader,
    TextureStage,
    Vec2
)


# Classes
# =======
class SkyDome(object):
    sky_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )

    def __init__(self, horizon, zenith, cloud_tex, celestials_tex):
        # Set background color
        base.win.set_clear_color(horizon)

        # Load skydome mesh
        self.skydome = base.loader.load_model("meshes/DynamicSkyDome.gltf")
        self.skydome.find("**/DynamicSkyDome").node().set_bounds(OmniBoundingVolume())
        self.skydome.set_shader(self.sky_shader)
        self.set_horizon_color(horizon)
        self.set_zenith_color(zenith)
        self.set_cloud_texture(cloud_tex)
        self.set_cloud_scroll_vec(Vec2(.01, 0))
        self.set_cloud_scale(Vec2(1, 1))
        self.set_celestial_texture(celestials_tex)
        self.set_celestial_scroll_vec(Vec2(.001, 0))
        self.skydome.set_attrib(DepthTestAttrib.make(DepthTestAttrib.M_less_equal))
        self.skydome.reparent_to(base.render)

    def set_horizon_color(self, color):
        self.skydome.set_shader_input("horizonColor", color)

    def set_zenith_color(self, color):
        self.skydome.set_shader_input("zenithColor", color)

    def set_cloud_texture(self, tex):
        stage1 = TextureStage("Clouds")
        stage1.set_sort(1)
        self.skydome.set_texture(stage1, tex)

    def set_cloud_scroll_vec(self, vec):
        self.skydome.set_shader_input("cloudScrollVec", vec)

    def set_cloud_scale(self, scale):
        self.skydome.set_shader_input("cloudScale", scale)

    def set_celestial_texture(self, tex):
        stage2 = TextureStage("Celestials")
        stage2.set_sort(2)
        self.skydome.set_texture(stage2, tex)

    def set_celestial_scroll_vec(self, vec):
        self.skydome.set_shader_input("celestialScrollVec", vec)
