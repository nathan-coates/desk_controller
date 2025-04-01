package player

import (
	"bufio"
	"bytes"
	"os"
	"strings"
)

func updateEnvFile(refreshToken, accessToken string) error {
	var builder bytes.Buffer

	file, err := os.Open(".env")
	if err != nil {
		return err
	}

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "SPOTIFY_REFRESH_TOKEN") {
			builder.WriteString("SPOTIFY_REFRESH_TOKEN=")
			builder.WriteString(refreshToken)
			builder.WriteString("\n")
		} else if strings.HasPrefix(line, "SPOTIFY_ACCESS_TOKEN") {
			builder.WriteString("SPOTIFY_ACCESS_TOKEN=")
			builder.WriteString(accessToken)
			builder.WriteString("\n")
		} else {
			builder.WriteString(line)
			builder.WriteString("\n")
		}
	}

	err = scanner.Err()
	if err != nil {
		return err
	}

	err = file.Close()
	if err != nil {
		return err
	}

	return os.WriteFile(".env", builder.Bytes(), os.ModePerm)
}
