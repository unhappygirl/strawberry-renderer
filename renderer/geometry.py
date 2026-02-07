
import numpy as np


IDENTITY_3 = np.identity(3)
IDENTITY_4 = np.identity(4)


def ROTATION_MATRIX_X(a):
    return np.array([[1, 0, 0, 0],
                     [0, np.cos(a), -np.sin(a), 0],
                     [0, np.sin(a), np.cos(a), 0],
                     [0, 0, 0, 1]], dtype=np.float32)


def ROTATION_MATRIX_Y(a):
    return np.array([[np.cos(a), 0, np.sin(a), 0],
                     [0, 1, 0, 0],
                     [-np.sin(a), 0, np.cos(a), 0],
                     [0, 0, 0, 1]], dtype=np.float32)


def ROTATION_MATRIX_Z(a):
    return np.array([[np.cos(a), -np.sin(a), 0, 0],
                     [np.sin(a), np.cos(a), 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]], dtype=np.float32)


def TRANSLATION_MATRIX_(tvec):
    return np.array([[1, 0, 0, tvec[0]],
                     [0, 1, 0, tvec[1]],
                     [0, 0, 1, tvec[2]],
                     [0, 0, 0, 1]], dtype=np.float32)


def np_normalize(vec):
    return vec / np.linalg.norm(vec)


def plain_normalize(vec):
    norm = sum([x**2 for x in vec]) ** 0.5
    return [x / norm for x in vec]


def plain_dot(v1, v2):
    return sum([v1[i] * v2[i] for i in range(len(v1))])


def plain_dot3(v13, v23):
    return v13[0]*v23[0] + v13[1]*v23[1] + v13[2]*v23[2]


class Primitive:
    def __init__(self, vertices, normals=None):
        v = np.asarray(vertices, dtype=np.float32)
        self.vertex_count = v.shape[0]
        ones = np.ones((self.vertex_count, 1), dtype=np.float32)

        # make the vertices column major
        self.trans_vertices = (np.concatenate([v, ones], axis=1))
        self.vertices = self.trans_vertices.T
        self.plain_vertices = self.trans_vertices.tolist()
        self.center = sum(self.trans_vertices[:, 0:3]) / self.vertex_count
        self.plain_center = self.center.tolist()

        self.init_normals(normals)
        self.init_buffers()

    def init_buffers(self):
        # final screen coordinates buffer
        self.screen_buffer = np.empty((2, self.vertex_count), dtype=np.float32)
        # clip space buffer for clipping
        self.clip_buffer = np.empty((4, self.vertex_count), dtype=np.float32)

    def init_normals(self, normals):
        if not normals:
            self.normals = self.generate_normals()
        else:
            self.normals = np.asarray(normals, dtype=np.float32)
        self.average_normal = sum(self.normals) / self.vertex_count
        self.plain_average_normal = self.average_normal.tolist()

    def generate_normals(self):
        p1, p2, p3, *_ = self.trans_vertices
        v1 = np_normalize(p2 - p1)
        v2 = np_normalize(p3 - p2)
        return np.array(
            [np.cross(v1[: 3], v2[: 3]), ] * self.vertex_count,
            dtype=np.float32)

    def translate(self, tvec):
        self.vertices = TRANSLATION_MATRIX_(tvec).dot(self.vertices)
        self.center += tvec
        self.plain_center = self.center.tolist()

    def rotate(self, rm, rpoint=(0, 0, 0)):
        # translate to origin
        self.translate([-x for x in rpoint])
        # rotate
        self.vertices = rm.dot(self.vertices)
        # translate back
        self.translate(rpoint)
        
    def average_w(self):
        return sum(self.clip_buffer[-1].tolist()) / self.vertex_count
    
    def average_clip_z(self):
        return sum(self.clip_buffer[-2].tolist()) / self.vertex_count
    
    def average_clip_x(self):
        return sum(self.clip_buffer[0].tolist()) / self.vertex_count

    def average_clip_y(self):
        return sum(self.clip_buffer[1].tolist()) / self.vertex_count

    def __repr__(self):
        return f"<Primitive object with center: {self.center}"


class Mesh:
    def __init__(self, *primitives, color, model_matrix):
        self.primitives = primitives
        self.model = model_matrix
        self.color = color

    def translate(self, tvec):
        for p in self.primitives:
            p.translate(tvec)

    def rotate(self, rm, rpoint=(0, 0, 0)):
        for p in self.primitives:
            p.rotate(rm, rpoint=rpoint)
