from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    GeoMipTerrain,
    Material,
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
        self.ambient_light.node().set_color(Vec4(.2, .2, .2, 1))
        self.render.set_light(self.ambient_light)

        self.sun = self.render.attach_new_node(DirectionalLight("Sun"))
        self.sun.set_hpr(45, -45, 0)
        self.render.set_light(self.sun)

        # Create materials
        terrain_mat = Material("Terrain")
        terrain_mat.set_base_color(Vec4(0, .5, 0, 1))
        terrain_mat.set_metallic(0)
        terrain_mat.set_emission(Vec4(0, 0, 0, 1))
        terrain_mat.set_roughness(.8)
        terrain_mat.set_refractive_index(1.5)

        # Load terrain
        self.terrain = GeoMipTerrain("Terrain")
        self.terrain.set_heightfield("images/Heightmap.png")
        self.terrain.set_block_size(32)
        self.terrain.set_focal_point(self.camera)

        self.terrain.get_root().set_sz(128)
        self.terrain.get_root().set_pos(-256, 0, -64)
        self.terrain.get_root().set_material(terrain_mat)

        self.terrain.generate()
        self.terrain.get_root().reparent_to(self.render)

        # Add update task
        self.task_mgr.add(self.update, "update")

    def update(self, task):
        # Update terrain
        self.terrain.update()
        return task.cont


# Entry Point
# ===========
if __name__ == "__main__":
    TerrainDemo().run()
