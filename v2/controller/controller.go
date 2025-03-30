package controller

import (
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
)

type App struct {
	app   shared.App
	left  *shared.App
	right *shared.App
	menu  bool
}

type Controller struct {
	currentApp *App
	backApp    *App
	topHb      shared.HitBox
	menuHb     shared.HitBox
	leftHb     shared.HitBox
	rightHb    shared.HitBox
	apps       []*App
}

func New(kvmApp, menuApp shared.App) *Controller {
	c := &Controller{
		apps: []*App{
			{
				app:  menuApp,
				menu: false,
			},
			{
				app:  kvmApp,
				menu: true,
			},
		},
	}

	c.currentApp = c.apps[1]

	return c
}

func (c *Controller) CurrentDisplay() string {
	return c.currentApp.app.Display()
}

func (c *Controller) PendingUpdate() *shared.Result {
	return c.currentApp.app.PendingUpdate()
}

func (c *Controller) TouchEvent(x, y, s int) bool {
	coords := shared.NewTouchCoordinates(x, y, s)
	log.Printf("touch coords internally: %v", coords)

	topBarCheck := coords.In(c.topHb)
	log.Printf("topBarCheck: %v", topBarCheck)
	if topBarCheck {
		if c.currentApp.menu {
			menuCheck := coords.In(c.menuHb)
			if menuCheck {
				log.Println("menu was clicked")
				c.backApp = c.currentApp
				c.currentApp = c.apps[0]
				return true
			}
		} else {
			leftBarCheck := coords.In(c.leftHb)
			if leftBarCheck {
				c.currentApp = c.backApp
				return true
			}
		}

		//if c.currentApp.left != nil {
		//	leftBarCheck := coords.In(c.leftHb)
		//	if leftBarCheck {
		//		c.currentApp = c.currentApp.left
		//		return 1
		//	}
		//}
		//
		//if c.currentApp.right != nil {
		//	rightBarCheck := coords.In(c.rightHb)
		//	if rightBarCheck {
		//		c.currentApp = c.currentApp.right
		//		return 1
		//	}
		//}

		log.Println("top bar was clicked but no button")
		return false
	}

	return c.currentApp.app.TouchEvent(coords)
}

func (c *Controller) Cleanup() {
	for _, app := range c.apps {
		app.app.Cleanup()
	}
}
