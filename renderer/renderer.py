

from .geometry import *
from .lighting import *
from . import LOGGING_FORMAT, dataclass, pygame, logger, logging


# from geometry import *
# from dataclasses import dataclass
# import pygame


@dataclass
class Viewport:
    width: float
    height: float
    z_distance: float


class Camera:
    def __init__(self, pos, viewport: Viewport, far, forward, world_up=(0, 1, 0)):
        self.pos = pos
        self.viewport = viewport
        self.far = far
        self.forward = np.asarray(forward, dtype=np.float32)
        self.world_up = np.asarray(world_up, dtype=np.float32)
        self.near = self.viewport.z_distance

    def translate(self, tvec):
        self.pos += tvec

    def build_basis(self):
        right = np.cross(self.world_up, self.forward)
        up = np.cross(self.forward, right)
        self.basis = right, up, self.forward

    def yaw(self, angle):
        self.forward = ROTATION_MATRIX_Y(angle)[0: 3, 0: 3].dot(self.forward)

    def pitch(self, angle):
        self.forward = ROTATION_MATRIX_X(angle)[0: 3, 0: 3].dot(self.forward)

    def roll(self, angle):
        self.world_up = ROTATION_MATRIX_Z(angle)[0: 3, 0: 3].dot(self.forward)

    def view_matrix(self):
        self.build_basis()
        a1, a2, a3 = self.basis
        return np.array([[*a1, np.dot(np.multiply(a1, -1), self.pos)],
                         [*a2, np.dot(np.multiply(a2, -1), self.pos)],
                         [*a3, np.dot(np.multiply(a3, -1), self.pos)],
                         [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)

    def projection_matrix(self):
        vw, vh = self.viewport.width, self.viewport.height
        f, n = self.far, self.near
        return np.array([[2/vw, 0.0, 0.0, 0.0],
                         [0.0, 2/vh, 0.0, 0.0],
                         [0.0, 0.0, (f+n)/(n*(f-n)), 2*f/(n-f)],
                         [0.0, 0.0, 1/n, 0.0]], dtype=np.float32)

    def view_projection_matrix(self):
        return self.projection_matrix() @ self.view_matrix()


class Renderer:
    KEY_ACTION_MAP = {
        pygame.K_a: lambda self: self.translate_camera(-self.camera.basis[0]*8),
        pygame.K_d: lambda self: self.translate_camera(self.camera.basis[0]*8),
        pygame.K_w: lambda self: self.translate_camera(self.camera.basis[2]*8),
        pygame.K_s: lambda self: self.translate_camera(-self.camera.basis[2]*8),
        pygame.K_f: lambda self: self.translate_camera(-self.camera.basis[1]*8),
        pygame.K_r: lambda self: self.translate_camera(self.camera.basis[1]*8),
    }

    def __init__(self, camera: Camera, pysurface: pygame.Surface, debug=False):
        self.camera = camera
        self.screen = pysurface
        self.width, self.height = self.screen.get_size()
        self.screen_scale = min(self.width, self.height) * 0.5

        self.tmp = np.empty(4, dtype=np.float32)
        wh, hh = self.width / 2, self.height / 2
        ss = self.screen_scale

        self.screen_matrix = np.array(
            [[ss, 0, 0, wh],
             [0, -ss, 0, hh],
             [0, 0, 1, 0],
             [0, 0, 0, 1]], dtype=np.float32)
        
        self.view_projection_matrix = self.camera.view_projection_matrix()

        if debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format=LOGGING_FORMAT)

    def move_cam_to(self):
        pass

    def translate_camera(self, tvec):
        self.camera.translate(tvec)
        self.view_projection_matrix = self.camera.view_projection_matrix()

    def camera_yaw(self, angle):
        self.camera.yaw(angle)
        self.view_projection_matrix = self.camera.view_projection_matrix()

    def camera_pitch(self, angle):
        self.camera.pitch(angle)
        self.view_projection_matrix = self.camera.view_projection_matrix()

    def camera_roll(self, angle):
        self.camera.roll(angle)
        self.view_projection_matrix = self.camera.view_projection_matrix()

    # hot path: no hard allocation, no initialization. Preallocate.

    # todo: save this func from bs numpy overhead
    def is_back_face(self, primitive):
        p = primitive.plain_center
        c = self.camera.pos
        tc = [c[0] - p[0], c[1] - p[1], c[2] - p[2]]
        pac = primitive.plain_average_normal
        result = (pac[0] * tc[0] + pac[1] * tc[1] + pac[2] * tc[2]) <= 0
        return result
    
    def to_screen_space(self, primitive):
        primitive.screen_buffer[0: 2] = (self.screen_matrix @ primitive.clip_buffer)[0: 2] 

    def project_primitive(self, primitive: Primitive):
        self.view_projection_matrix.dot(primitive.vertices,
                            out=primitive.clip_buffer)

        self.to_screen_space(primitive)
        
        # perspective divide
        primitive.screen_buffer /= primitive.clip_buffer[3]

    # expects the primitive's clip buffer to be populated.
    def clip_test_flat(self, primitive):
        average_w = primitive.average_w()
        if not (-average_w < primitive.average_clip_z() < average_w):
            return False
        if not (-average_w < primitive.average_clip_x() < average_w):
            return False
        if not (-average_w < primitive.average_clip_y() < average_w):
            return False
        return True

    def project_mesh(self, mesh: Mesh):
        for prim in mesh.primitives:
            self.project_primitive(prim)

    # render per primitive basis
    def draw_mesh_flat(self, mesh, flat_shader=None, wireframe=False):
        # painter's algorithm
        primitives = sorted(
            mesh.primitives, key=lambda p: p.average_w(), reverse=True)
        for prim in primitives:
            if self.is_back_face(prim) or not self.clip_test_flat(prim):
                continue
            self.draw_primitive_flat(
                prim, mesh.color, flat_shader=flat_shader, wireframe=wireframe)

    def draw_primitive_flat(self, primitive: Primitive,
                            color, flat_shader, wireframe=False):
        if wireframe:
            pygame.draw.lines(self.screen, color, closed=True,
                              points=primitive.screen_buffer.T.tolist())
        else:
            primitive_color = flat_shader(
                color, primitive) if flat_shader else color
            pygame.draw.polygon(self.screen, primitive_color,
                                points=primitive.screen_buffer.T.tolist())

    # end of hot path

    def clear_screen(self, color=(0, 0, 0)):
        self.screen.fill((255, 255, 255))
        self.screen.fill(color)

    # input handlers

    def handle_mouse_events(self):
        rx, ry = pygame.mouse.get_rel()
        if not (rx or ry):
            return
        self.camera_yaw(rx * np.radians(0.1))
        self.camera_pitch(ry * np.radians(0.1))

    def handle_keyboard_events(self, pg_kmap):
        for key in self.KEY_ACTION_MAP:
            if pg_kmap[key]:
                action = self.KEY_ACTION_MAP[key]
                action(self)

    def handle_input_events(self):
        # pump events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        #
        kmap = pygame.key.get_pressed()
        self.handle_keyboard_events(kmap)
        self.handle_mouse_events()
