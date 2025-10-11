from panda3d.core import (
    DepthTestAttrib,
    OmniBoundingVolume,
    Shader
)


# Classes
# =======
class SkyDome(object):
    sky_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )

    def __init__(self, horizon):
        # Set background color
        base.win.set_clear_color(pow(horizon, 2.2 / 1))

        # Load skydome mesh
        self.skydome = base.loader.load_model("meshes/SkyDome.gltf")
        self.skydome.find("**/SkyDome").node().set_bounds(OmniBoundingVolume())
        self.skydome.set_shader(self.sky_shader)
        self.skydome.set_attrib(DepthTestAttrib.make(DepthTestAttrib.M_less_equal))
        self.skydome.reparent_to(base.render)
