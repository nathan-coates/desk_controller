package menu

import (
	"embed"
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
)

//go:embed *.bmp
var images embed.FS

var (
	MenuBase     string
	MenuRefresh  string
	MenuRestart  string
	MenuShutdown string
)

func init() {
	mapping, err := shared.WriteImagesToFile(images)
	if err != nil {
		log.Fatal(err)
	}

	MenuBase = mapping["Menu_base.bmp"]
	MenuRefresh = mapping["Menu_refresh.bmp"]
	MenuRestart = mapping["Menu_restart.bmp"]
	MenuShutdown = mapping["Menu_shutdown.bmp"]
}
