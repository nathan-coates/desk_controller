package lights

import (
	"embed"
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
)

//go:embed *.bmp
var images embed.FS

var (
	LightsdFLvFbdF string
	LightsdFLvFbdO string
	LightsdFLvObdF string
	LightsdFLvObdO string
	LightsdOLvFbdF string
	LightsdOLvFbdO string
	LightsdOLvObdF string
	LightsdOLvObdO string
	LightsError    string
)

func init() {
	mapping, err := shared.WriteImagesToFile(images)
	if err != nil {
		log.Fatal(err)
	}

	LightsdFLvFbdF = mapping["Lights_df-lvf-bdf.bmp"]
	LightsdFLvFbdO = mapping["Lights_df-lvf-bdo.bmp"]
	LightsdFLvObdF = mapping["Lights_df-lvo-bdf.bmp"]
	LightsdFLvObdO = mapping["Lights_df-lvo-bdo.bmp"]
	LightsdOLvFbdF = mapping["Lights_do-lvf-bdf.bmp"]
	LightsdOLvFbdO = mapping["Lights_do-lvf-bdo.bmp"]
	LightsdOLvObdF = mapping["Lights_do-lvo-bdf.bmp"]
	LightsdOLvObdO = mapping["Lights_do-lvo-bdo.bmp"]
	LightsError = mapping["Error_lights.bmp"]

}
