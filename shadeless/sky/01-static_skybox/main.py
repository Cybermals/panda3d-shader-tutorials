from direct.showbase.ShowBase import ShowBase
from panda3d.core import SamplerState

from sky import SkyBox


# Classes
# =======
class SkyDemo(ShowBase):
    def __init__(self):
        # Call the base constructor
        ShowBase.__init__(self)

        # Load cubemap sky texture
        self.sky_tex = self.loader.load_cube_map("images/TestSky-#.png")
        self.sky_tex.minfilter = SamplerState.FT_linear_mipmap_linear
        self.sky_tex.magfilter = SamplerState.FT_linear_mipmap_linear

        # Create sky
        self.sky = SkyBox(self.sky_tex)


# Entry Point
if __name__ == "__main__":
    SkyDemo().run()
