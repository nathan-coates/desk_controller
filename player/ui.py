from enum import Enum

import shared
from shared import get_image_path

IMAGES_DIR = shared.get_images_dir(__file__)


class ImagesMapping(str, Enum):
    player_paused = get_image_path(IMAGES_DIR, "Player_paused.bmp")
    player_playing = get_image_path(IMAGES_DIR, "Player_playing.bmp")
    player_playing_back = get_image_path(IMAGES_DIR, "Player_playing_back.bmp")
    player_playing_next = get_image_path(IMAGES_DIR, "Player_playing_next.bmp")
    error = get_image_path(IMAGES_DIR, "Error_player.bmp")
