from direct.showbase.ShowBase import ShowBase


# Application Class
# =================
class TerrainDemo(ShowBase):
    def __init__(self):
        # Call base constructor
        ShowBase.__init__(self)

        # Load terrain
        self.terrain = self.loader.load_model("meshes/Terrain")
        self.terrain.set_scale(256, 256, 256)
        self.terrain.set_pos(0, 261, 0)
        self.terrain.reparent_to(self.render)


# Entry Point
# ===========
if __name__ == "__main__":
    TerrainDemo().run()
