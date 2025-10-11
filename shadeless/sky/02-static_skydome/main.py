from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    load_prc_file,
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

        # Create skydome
        self.skydome = SkyDome(Vec4(0, .61, 1, 1))


# Entry Point
if __name__ == "__main__":
    SkyDemo().run()
