
from .geometry import Primitive, np_normalize, np, plain_normalize
from enum import Enum


class LightType(Enum):
    DIRECTIONAL = 2
    POINT = 1
    AMBIENT = 0


class Light:
    def __init__(self, type: LightType, pos=None,
                 color=(255, 255, 255), direction=None, ambience=None):
        self.type = type
        self.pos = pos
        self.color = color
        if direction:
            self.direction = np_normalize(np.asarray(direction))
        self.ambience = ambience

    def vec_to_primitive(self, primitive: Primitive):
        if self.type is LightType.POINT:
            return plain_normalize([self.pos[0] - primitive.plain_center[0],
                                    self.pos[1] - primitive.plain_center[1],
                                    self.pos[2] - primitive.plain_center[2]])

        elif self.type is LightType.DIRECTIONAL:
            return -self.direction
        
    def translate(self, tvec):
        if self.pos:
            for i in range(3):
                self.pos[i] += tvec[i]
        
