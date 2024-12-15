from direct.showbase.ShowBase import ShowBase


# Application Class
# =================
class ShaderDemo(ShowBase):
    def __init__(self):
        # Call the base constructor
        ShowBase.__init__(self)

        # Load sphere mesh
        self.sphere = self.loader.load_model("meshes/Sphere")
        self.sphere.set_pos(0, 5, 0)
        self.sphere.reparent_to(self.render)


# Entry Point
# ===========
if __name__ == "__main__":
    ShaderDemo().run()
