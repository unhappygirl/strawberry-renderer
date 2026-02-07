

from . import dataclass
from .geometry import Mesh, Primitive

#from dataclasses import dataclass
#from geometry import Mesh, Primitive


@dataclass
class ParsedOBJ:
    vertices: list
    texcoords: list
    normals: list
    faces: list


# an wavefront obj parser
class ObjParser:
    def __init__(self, obj_path):
        with open(obj_path, 'r') as f:
            self.lines = f.readlines()
        self.parsed = ParsedOBJ([], [], [], [])

    def line_resolution(self, head):
        if head == "v":
            return self.parsed.vertices
        elif head == "vt":
            return self.parsed.texcoords
        elif head == "vn":
            return self.parsed.normals
        elif head == "f":
            return self.parsed.faces
        else:
            return None

    def parse_data(self, head, data):
        if head in ("v", "vt", "vn"):
            return [float(x) for x in data]
        elif head == "f":
            face = []
            for f in data:
                if "/" not in f:
                    indices = [f, "", ""]
                else:
                    indices = f.split("/")
                # indexing starts from 1 in obj files
                face.append([int(i) - 1 if i.isdigit()
                            else None for i in indices])
            return face
        else:
            return None

    def parse(self):
        for line in self.lines:
            # comment or empty, ignore
            if line.startswith("#") or ((s := line.strip()) == ""):
                continue
            sl = s.split()
            head, data = sl[0], sl[1: len(sl)]
            rlist = self.line_resolution(head)
            if rlist is None:
                continue
            else:
                rlist.append(self.parse_data(head, data))

    def dump_to_Mesh(self):
        primitives = list()
        for face in self.parsed.faces:
            face_vertices = list()
            normals = list()
            for data in face:
                if len(data) != 3:
                    data += [None] * (3 - len(data))
                vi, tvi, ni = data
                rvertex = self.parsed.vertices[vi]
                face_vertices.append(tuple(rvertex))
                if ni is not None:
                    normals.append(self.parsed.normals[ni])
            primitives.append(Primitive(vertices=face_vertices, normals=normals))
        return Mesh(*primitives, color=(255, 255, 255), model_matrix=None)
