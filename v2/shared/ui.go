package shared

import (
	"embed"
	"io/fs"
	"log"
	"os"
	"path/filepath"
)

const IMAGES = "images"

func WriteImagesToFile(images embed.FS) (map[string]string, error) {
	imagePaths := make(map[string]string)

	_, err := os.Stat(IMAGES)
	if err != nil {
		if os.IsNotExist(err) {
			err = os.MkdirAll(IMAGES, 0755)
			if err != nil {
				return imagePaths, err
			}
		} else {
			return imagePaths, err
		}
	}

	return imagePaths, fs.WalkDir(images, ".", func(path string, d fs.DirEntry, err error) error {
		if d.IsDir() {
			log.Println(path)
			return nil
		}

		content, err := images.ReadFile(path)
		if err != nil {
			return err
		}

		fullPath := filepath.Join(IMAGES, path)

		_, err = os.Stat(fullPath)
		if err != nil {
			if os.IsNotExist(err) {
				err = os.WriteFile(fullPath, content, 0755)
				if err != nil {
					return err
				}
			} else {
				return err
			}
		}

		imagePaths[path] = "./" + fullPath
		return nil
	})
}
