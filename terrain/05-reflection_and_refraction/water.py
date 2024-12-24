from panda3d.core import (
    ClipPlaneAttrib,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GraphicsOutput,
    Material,
    Plane,
    PlaneNode,
    SamplerState,
    Shader,
    Texture,
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
            self.water_mat.set_ambient(Vec4(0, .225, .8, 1))
            self.water_mat.set_diffuse(Vec4(0, .225, .8, 1))
            self.water_mat.set_specular(Vec3(.5, .5, .5))
            self.water_mat.set_shininess(32)

        # Get the default camera lens
        cam_lens = base.cam.node().get_lens()

        # Create refraction buffer. Using (0, 0) for the size indicates that the size of the buffer should
        # be synced with the main window.
        self.refract_buf = base.win.make_texture_buffer("WaterRefractionBuffer", 0, 0)
        self.refract_buf.set_sort(-100)
        self.refract_buf.add_render_texture(
            Texture("RefractionDepth"),
            GraphicsOutput.RTM_bind_or_copy,
            GraphicsOutput.RTP_depth
        )
        self.refract_tex = self.refract_buf.get_texture()
        self.refract_depth_tex = self.refract_buf.get_texture(1)
        self.refract_tex.wrap_u = SamplerState.WM_repeat
        self.refract_tex.wrap_v = SamplerState.WM_repeat
        
        self.refract_cam = base.make_camera(self.refract_buf, lens=cam_lens)
        self.refract_cam.reparent_to(base.render)

        # Create reflection buffer. Using (0, 0) for the size indicates that the size of the buffer should
        # be synced with the main window.
        self.reflect_buf = base.win.make_texture_buffer("WaterReflectionBuffer", 0, 0)
        self.reflect_buf.set_sort(-100)
        self.reflect_tex = self.reflect_buf.get_texture()
        self.reflect_tex.wrap_u = SamplerState.WM_repeat
        self.reflect_tex.wrap_v = SamplerState.WM_repeat
        
        self.reflect_cam = base.make_camera(self.reflect_buf, lens=cam_lens)
        self.reflect_cam.reparent_to(base.render)

        # Register water camera update task
        base.task_mgr.add(self.update_cameras, "update_water_cameras")

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

        # Configure refraction clipping plane
        self.refract_clip_plane = self.plane.attach_new_node(PlaneNode(
            "WaterRefractClipPlane",
            Plane(0, 0, -1, -.001)
        ))
        clip_state = ClipPlaneAttrib.make_default().add_on_plane(self.refract_clip_plane)
        self.refract_cam.node().set_initial_state(clip_state)

        # Configure reflection clipping plane
        self.reflect_clip_plane = self.plane.attach_new_node(PlaneNode(
            "WaterReflectClipPlane",
            Plane(0, 0, 1, -.001)
        ))
        clip_state = ClipPlaneAttrib.make_default().add_on_plane(self.reflect_clip_plane)
        self.reflect_cam.node().set_initial_state(clip_state)

    def update_cameras(self, task):
        # Update refraction and reflection cameras
        self.refract_cam.set_transform(base.camera.get_transform())

        self.reflect_cam.set_transform(base.camera.get_transform())
        cam_height = base.camera.get_z()
        dist = cam_height - self.plane.get_z()
        self.reflect_cam.set_z(self.reflect_cam.get_z() - dist * 2)
        self.reflect_cam.set_p(-self.reflect_cam.get_p())
        self.reflect_cam.set_r(self.reflect_cam.get_r() + 180)
        return task.cont
