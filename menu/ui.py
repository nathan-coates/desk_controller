from enum import Enum

import shared
from shared import get_image_path

IMAGES_DIR = shared.get_images_dir(__file__)


class ImagesMapping(str, Enum):
    menu_base = get_image_path(IMAGES_DIR, "Menu_base.bmp")
    menu_refresh = get_image_path(IMAGES_DIR, "Menu_refresh.bmp")
    menu_shutdown = get_image_path(IMAGES_DIR, "Menu_shutdown.bmp")
    menu_restart = get_image_path(IMAGES_DIR, "Menu_restart.bmp")
