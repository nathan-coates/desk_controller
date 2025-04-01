package player

import (
	"embed"
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
)

//go:embed *.bmp
var images embed.FS

var (
	PlayerPaused      string
	PlayerPlaying     string
	PlayerPlayingBack string
	PlayerPlayingNext string
	PlayerError       string
)

func init() {
	mapping, err := shared.WriteImagesToFile(images)
	if err != nil {
		log.Fatal(err)
	}

	PlayerPaused = mapping["Player_paused.bmp"]
	PlayerPlaying = mapping["Player_playing.bmp"]
	PlayerPlayingBack = mapping["Player_playing_back.bmp"]
	PlayerPlayingNext = mapping["Player_playing_next.bmp"]
	PlayerError = mapping["Error_player.bmp"]
}
