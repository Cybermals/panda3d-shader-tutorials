from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file,
    SamplerState,
    Vec2,
    Vec4
)

from sky import SkyDome


# Classes
# =======
class SkyDemo(ShowBase):
    def __init__(self):
        # Load config file
        load_prc_file("settings.prc")

        # Call the base constructor
        ShowBase.__init__(self)

        # Load textures
        self.cloud_tex = self.loader.load_texture("images/Clouds.png")
        self.cloud_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.cloud_tex.magfilter = SamplerState.FT_linear_mipmap_linear
        self.cloud_tex.wrap_u = SamplerState.WM_repeat
        self.cloud_tex.wrap_v = SamplerState.WM_repeat

        self.celestials_tex = self.loader.load_texture("images/Celestials.png")
        self.celestials_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.celestials_tex.magfilter = SamplerState.FT_linear_mipmap_linear
        self.celestials_tex.wrap_u = SamplerState.WM_repeat
        self.celestials_tex.wrap_v = SamplerState.WM_repeat

        # Create skydome
        self.skydome = SkyDome(
            Vec4(1, .5, .1, 1),
            Vec4(0, .61, 1, 1),
            self.cloud_tex,
            self.celestials_tex
        )
        self.skydome.set_cloud_scale(Vec2(.5, .5))


# Entry Point
if __name__ == "__main__":
    SkyDemo().run()
