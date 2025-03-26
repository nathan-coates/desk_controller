from pathlib import Path


def get_images_dir(path: str) -> Path:
    module_dir = Path(path).resolve().parent
    return module_dir / "images"


def get_image_path(images_dir: Path, image: str) -> str:
    return str(images_dir / image)
