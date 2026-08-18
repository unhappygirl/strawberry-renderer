
from .renderer import *
from .wavefront_obj import *
from .lighting import Light, LightType
from .shading import FlatShader
import sys
import cProfile
import pstats


def test():
    camera = Camera((0, 0, 0), Viewport(2, 2, 2), forward=(0, 0, 1), far=2000)
    screen = pygame.display.set_mode((800, 800))
    debug = sys.argv[2] in ["debug", "--debug",
                            "-debug"] if len(sys.argv) > 2 else False
    myrenderer = Renderer(camera=camera, pysurface=screen, debug=debug)
    lights = [Light(LightType(1), pos=[10, 0, -10]),
              Light(LightType(0), ambience=0.2)]

    def myshader(c, p): return FlatShader.flat_shade(c, p, lights)
    parser = ObjParser(sys.argv[1])
    parser.parse()
    test_mesh = parser.dump_to_Mesh()
    test_mesh.color = (0xFF, 0xFF, 0xFF)
    test_mesh.translate((0, 0, 50))

    clock = pygame.time.Clock()

    while True:
        myrenderer.clear_screen(color=(0, 0, 0))
        myrenderer.project_mesh(test_mesh)
        myrenderer.draw_mesh_flat(
            test_mesh, wireframe=False, flat_shader=myshader)
        test_mesh.rotate(ROTATION_MATRIX_Y(np.radians(5)), rpoint=test_mesh.center)
        pygame.display.flip()
        clock.tick(60)
        myrenderer.handle_input_events()


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable(subcalls=True, builtins=True)
    try:
        test()
    finally:
        profiler.disable()
        profiler.dump_stats("strawberry.prof")
        s = pstats.Stats("strawberry.prof")
        s.strip_dirs().sort_stats("tottime").print_callees("to_surface")
