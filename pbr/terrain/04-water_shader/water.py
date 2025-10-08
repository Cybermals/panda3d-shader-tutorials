from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    Material,
    Shader,
    Vec3,
    Vec4
)


# Classes
# =======
class WaterPlane(object):
    water_shader = Shader.load(
        Shader.SL_GLSL,
        "shaders/Water.vert.glsl",
        "shaders/Water.frag.glsl"
    )
    water_mat = None
    plane_mesh = None

    def __init__(self, pos=Vec3(), heading=0, scale=Vec3(1, 1, 1)):
        # Initialize water material if necessary
        if self.water_mat is None:
            WaterPlane.water_mat = Material()
            self.water_mat.set_base_color(Vec4(0, .225, .8, 1))
            self.water_mat.set_metallic(0)
            self.water_mat.set_emission(Vec4(0, 0, 0, 1))
            self.water_mat.set_roughness(.2)
            self.water_mat.set_refractive_index(1)

        # Initialize plane mesh if necessary
        if self.plane_mesh is None:
            # Get V3N3T2 format
            vtx_format = GeomVertexFormat.get_v3()

            # Allocate vertex data
            vertices = GeomVertexData("WaterPlane", vtx_format, Geom.UH_static)
            vertices.reserve_num_rows(4)

            # Write vertex data
            vertex = GeomVertexWriter(vertices, "vertex")
            vertex.add_data3(-1, 1, 0)
            vertex.add_data3(1, 1, 0)
            vertex.add_data3(-1, -1, 0)
            vertex.add_data3(1, -1, 0)

            # Allocate primitive data
            triangles = GeomTriangles(Geom.UH_static)
            triangles.reserve_num_vertices(6)

            # Write primitive data
            triangles.add_vertices(0, 2, 1)
            triangles.add_vertices(1, 2, 3)

            # Create plane mesh
            WaterPlane.plane_mesh = Geom(vertices)
            self.plane_mesh.add_primitive(triangles)

        # Create water plane
        self.plane = base.render.attach_new_node(GeomNode("WaterPlane"))
        self.plane.node().add_geom(self.plane_mesh)
        self.plane.set_pos(pos)
        self.plane.set_h(heading)
        self.plane.set_scale(scale)

        self.plane.set_shader(self.water_shader)

        self.plane.set_material(self.water_mat)
