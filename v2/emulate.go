//go:build darwin

package main

import (
	"fmt"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/joho/godotenv"
	"github.com/nathan-coates/desk_controller/v2/controller"
	"github.com/nathan-coates/desk_controller/v2/kvm"
	"github.com/nathan-coates/desk_controller/v2/lights"
	"github.com/nathan-coates/desk_controller/v2/menu"
	"github.com/nathan-coates/desk_controller/v2/player"
	"github.com/nathan-coates/desk_controller/v2/shared"
	"image"
	"image/png"
	_ "image/png"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
)

var imageMapping = make(map[string]image.Image)

func convert() error {
	folderPath := shared.IMAGES

	err := filepath.Walk(folderPath, func(filePath string, info os.FileInfo, err error) error {
		log.Println(filePath)
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if strings.ToLower(filepath.Ext(filePath)) == ".bmp" {
			pngFilename := strings.TrimSuffix(filePath, ".bmp") + ".png"

			cmd := exec.Command("convert", filePath, pngFilename)

			output, err := cmd.CombinedOutput()
			if err != nil {
				return fmt.Errorf("ImageMagick error for %s: %v, output: %s", filePath, err, string(output))
			}

			pngFile, err := os.Open(pngFilename)
			if err != nil {
				return err
			}

			pngImg, err := png.Decode(pngFile)
			if err != nil {
				return err
			}

			imageMapping["./"+filePath] = pngImg

			err = os.Remove(filePath)
			if err != nil {
				return err
			}

		} else {
			pngFile, err := os.Open(filePath)
			if err != nil {
				return err
			}

			pngImg, err := png.Decode(pngFile)
			if err != nil {
				return err
			}

			imageMapping["./"+filePath] = pngImg
		}
		return nil
	})
	return err
}

func cleanup() error {
	log.Println("Cleaning up...")

	folderPath := shared.IMAGES

	err := filepath.Walk(folderPath, func(filePath string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() && strings.ToLower(filepath.Ext(filePath)) == ".png" {
			err := os.Remove(filePath)
			if err != nil {
				return err
			}
		}

		return nil
	})
	return err
}

type mouseState int

const (
	mouseStateNone mouseState = iota
	mouseStatePressing
	mouseStateSettled
)

type Game struct {
	currentDisplay *ebiten.Image
	app            *controller.Controller
	mouseState     mouseState
	x              int
	y              int
}

func NewGame() *Game {
	k := kvm.New()
	p := player.New()
	l := lights.New()
	m := menu.New()

	g := &Game{
		app: controller.New(k, p, l, m),
		x:   -1,
		y:   -1,
	}

	err := convert()
	if err != nil {
		log.Fatal(err)
		return nil
	}

	g.currentDisplay = ebiten.NewImageFromImage(imageMapping[g.app.CurrentDisplay()])

	return g
}

func (g *Game) Update() error {
	switch g.mouseState {
	case mouseStateNone:
		if ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft) {
			g.mouseState = mouseStatePressing
		}
	case mouseStatePressing:
		if !ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft) {
			x, y := ebiten.CursorPosition()
			g.x = x
			g.y = y
			g.mouseState = mouseStateSettled

			response := g.app.TouchEvent(g.x, g.y, 0)
			if response {
				g.currentDisplay = ebiten.NewImageFromImage(imageMapping[g.app.CurrentDisplay()])
			}

			return nil
		}
	case mouseStateSettled:
		g.mouseState = mouseStateNone
		g.x = -1
		g.y = -1
	}

	pendingUpdate := g.app.PendingUpdate()
	if pendingUpdate != nil {
		g.currentDisplay = ebiten.NewImageFromImage(imageMapping[pendingUpdate.Display])
		shared.Pool.Put(pendingUpdate)
	}

	return nil
}

func (g *Game) Draw(screen *ebiten.Image) {
	screen.DrawImage(g.currentDisplay, nil)
}

func (g *Game) Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int) {
	return 250, 122
}

func (g *Game) Cleanup() {
	g.app.Cleanup()
}

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	ebiten.SetWindowSize(250, 122)
	ebiten.SetWindowTitle("Tester")
	game := NewGame()

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigs
		err := cleanup()
		if err != nil {
			log.Fatal(err)
		}
		game.Cleanup()
		os.Exit(0)
	}()

	rErr := ebiten.RunGame(game)
	if rErr != nil {
		err := cleanup()
		if err != nil {
			log.Fatal(err)
		}

		game.Cleanup()
		log.Fatal(rErr)
	}
}
