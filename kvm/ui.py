from enum import Enum

import shared
from shared import get_image_path

IMAGES_DIR = shared.get_images_dir(__file__)


class ImagesMapping(str, Enum):
    desktop = get_image_path(IMAGES_DIR, "KVM_desktop.bmp")
    mac_mini = get_image_path(IMAGES_DIR, "KVM_mac_mini.bmp")
    work_mac = get_image_path(IMAGES_DIR, "KVM_work_mac.bmp")
    error = get_image_path(IMAGES_DIR, "Error_kvm.bmp")
