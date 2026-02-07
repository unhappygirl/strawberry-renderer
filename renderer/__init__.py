

from dataclasses import dataclass
import pygame
import logging



logger = logging.getLogger("strawberry-renderer")
LOGGING_FORMAT = "[%(filename)s:%(lineno)s -> %(funcName)20s() ] %(message)s"

pygame.init()