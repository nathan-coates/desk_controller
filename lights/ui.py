from enum import Enum

import shared
from shared import get_image_path

IMAGES_DIR = shared.get_images_dir(__file__)


class ImagesMapping(str, Enum):
    lights_df_lvf_bdf = get_image_path(IMAGES_DIR, "Lights_df-lvf-bdf.bmp")
    lights_df_lvf_bdo = get_image_path(IMAGES_DIR, "Lights_df-lvf-bdo.bmp")
    lights_df_lvo_bdf = get_image_path(IMAGES_DIR, "Lights_df-lvo-bdf.bmp")
    lights_df_lvo_bdo = get_image_path(IMAGES_DIR, "Lights_df-lvo-bdo.bmp")
    lights_do_lvf_bdf = get_image_path(IMAGES_DIR, "Lights_do-lvf-bdf.bmp")
    lights_do_lvf_bdo = get_image_path(IMAGES_DIR, "Lights_do-lvf-bdo.bmp")
    lights_do_lvo_bdf = get_image_path(IMAGES_DIR, "Lights_do-lvo-bdf.bmp")
    lights_do_lvo_bdo = get_image_path(IMAGES_DIR, "Lights_do-lvo-bdo.bmp")
    lights_error = get_image_path(IMAGES_DIR, "Error_lights.bmp")
