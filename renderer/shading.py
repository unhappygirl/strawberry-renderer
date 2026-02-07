

from renderer.geometry import Primitive, plain_dot3
from renderer.lighting import Light, LightType
from . import logger

class FlatShader:
    @classmethod
    def flat_shade(cls, color, primitive: Primitive, lights: list[Light]):
        total_cosine = 0.0
        for light in lights:
            if light.type is LightType.AMBIENT:
                total_cosine += light.ambience
                continue
            cosine = plain_dot3(primitive.plain_average_normal,
                               light.vec_to_primitive(primitive))
            cosine = max(cosine, 0.0)
            total_cosine += cosine
        total_cosine = min(total_cosine, 1.0)
        return (total_cosine * color[0], total_cosine * color[1], total_cosine * color[2])