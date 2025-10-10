from panda3d.core import (
    DepthTestAttrib,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    OmniBoundingVolume,
    Shader
)


# Classes
# =======
class SkyBox(object):
    skybox_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Sky.vert.glsl",
        "shaders/Sky.frag.glsl"
    )
    skybox_mesh = None

    def __init__(self, texture):
        # Create skybox mesh
        if self.skybox_mesh is None:
            # Get vertex format
            vtx_format = GeomVertexFormat.get_v3()

            # Allocate vertex data
            vertices = GeomVertexData("Skybox", vtx_format, Geom.UH_static)
            vertices.reserve_num_rows(8)

            # Write vertex data
            vertex = GeomVertexWriter(vertices, "vertex")

            vertex.add_data3(-1, -1, -1)
            vertex.add_data3(1, -1, -1)
            vertex.add_data3(-1, 1, -1)
            vertex.add_data3(1, 1, -1)
            vertex.add_data3(-1, -1, 1)
            vertex.add_data3(1, -1, 1)
            vertex.add_data3(-1, 1, 1)
            vertex.add_data3(1, 1, 1)

            # Allocate primitive data
            triangles = GeomTriangles(Geom.UH_static)
            triangles.reserve_num_vertices(12)

            # Write primitive data
            triangles.add_vertices(4, 5, 1)
            triangles.add_vertices(1, 0, 4)
            triangles.add_vertices(2, 3, 7)
            triangles.add_vertices(7, 6, 2)
            triangles.add_vertices(2, 6, 4)
            triangles.add_vertices(4, 0, 2)
            triangles.add_vertices(1, 5, 7)
            triangles.add_vertices(7, 3, 1)
            triangles.add_vertices(4, 6, 7)
            triangles.add_vertices(7, 5, 4)
            triangles.add_vertices(0, 1, 3)
            triangles.add_vertices(3, 2, 0)

            # Create skybox mesh
            SkyBox.skybox_mesh = Geom(vertices)
            self.skybox_mesh.add_primitive(triangles)

        # Create skybox
        self.skybox = base.render.attach_new_node(GeomNode("Skybox"))
        self.skybox.node().add_geom(self.skybox_mesh)
        self.skybox.node().set_bounds(OmniBoundingVolume())
        self.skybox.set_shader(self.skybox_shader)
        self.skybox.set_texture(texture)
        depth_test_attrib = DepthTestAttrib.make(DepthTestAttrib.M_less_equal)
        self.skybox.set_attrib(depth_test_attrib)
