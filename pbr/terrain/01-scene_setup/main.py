from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Vec4
)
import simplepbr


# Application Class
# =================
class TerrainDemo(ShowBase):
    def __init__(self):
        # Call base constructor
        ShowBase.__init__(self)

        # Init shaders
        simplepbr.init()

        # Setup lighting
        self.ambient_light = self.render.attach_new_node(AmbientLight("AmbientLight"))
        self.ambient_light.node().set_color(Vec4(.04, .04, .04, 1))
        self.render.set_light(self.ambient_light)

        self.sun = self.render.attach_new_node(DirectionalLight("Sun"))
        self.sun.set_hpr(45, -45, 0)
        self.render.set_light(self.sun)

        # Load terrain
        self.terrain = self.loader.load_model("meshes/Terrain.gltf")
        self.terrain.set_scale(256, 256, 256)
        self.terrain.set_pos(0, 261, 0)
        self.terrain.reparent_to(self.render)


# Entry Point
# ===========
if __name__ == "__main__":
    TerrainDemo().run()
