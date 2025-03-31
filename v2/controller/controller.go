package controller

import (
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
)

type App struct {
	app   shared.App
	left  *App
	right *App
	menu  bool
}

type Controller struct {
	currentApp *App
	backApp    *App
	jobRunner  *shared.Runner
	apps       []*App
	topHb      shared.HitBox
	menuHb     shared.HitBox
	leftHb     shared.HitBox
	rightHb    shared.HitBox
	errBackHb  shared.HitBox
	errResHb   shared.HitBox
	errorState bool
}

func New(kvmApp, lightsApp, menuApp shared.App) *Controller {
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
			{
				app:  lightsApp,
				menu: true,
			},
		},
		topHb: shared.HitBox{
			XStart: 0,
			XEnd:   250,
			YStart: 0,
			YEnd:   13,
		},
		menuHb: shared.HitBox{
			XStart: 97,
			XEnd:   152,
			YStart: 2,
			YEnd:   13,
		},
		leftHb: shared.HitBox{
			XStart: 15,
			XEnd:   70,
			YStart: 2,
			YEnd:   13,
		},
		rightHb: shared.HitBox{
			XStart: 179,
			XEnd:   234,
			YStart: 2,
			YEnd:   13,
		},
		errBackHb: shared.HitBox{
			XStart: 66,
			XEnd:   119,
			YStart: 67,
			YEnd:   86,
		},
		errResHb: shared.HitBox{
			XStart: 130,
			XEnd:   183,
			YStart: 67,
			YEnd:   86,
		},
		jobRunner: shared.NewRunner(),
	}

	c.currentApp = c.apps[1]

	c.apps[1].right = c.apps[2]
	c.apps[2].left = c.apps[1]

	for _, app := range c.apps {
		job, duration := app.app.PeriodicJob()
		if job == nil {
			continue
		}

		c.jobRunner.AddJob(shared.NewJob(job, duration))
	}
	c.jobRunner.Run()

	return c
}

func (c *Controller) CurrentDisplay() string {
	return c.currentApp.app.Display()
}

func (c *Controller) Error() string {
	return c.currentApp.app.Error()
}

func (c *Controller) PendingUpdate() *shared.Result {
	result := c.currentApp.app.PendingUpdate()
	if result != nil && result.Result == shared.Error {
		c.errorState = true
	}

	return result
}

func (c *Controller) TouchEvent(x, y, s int) bool {
	coords := shared.NewTouchCoordinates(x, y, s)
	log.Printf("touch coords internally: %v", coords)

	if c.errorState {
		goBackCheck := coords.In(c.errBackHb)
		if goBackCheck {
			c.errorState = false
			return true
		}

		restart := coords.In(c.errResHb)
		if restart {
			// TODO - add restart logic
			c.errorState = false
			return true
		}

		return false
	}

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

		if c.currentApp.left != nil {
			leftBarCheck := coords.In(c.leftHb)
			if leftBarCheck {
				c.currentApp = c.currentApp.left
				return true
			}
		}

		if c.currentApp.right != nil {
			rightBarCheck := coords.In(c.rightHb)
			if rightBarCheck {
				c.currentApp = c.currentApp.right
				return true
			}
		}

		log.Println("top bar was clicked but no button")
		return false
	}

	return c.currentApp.app.TouchEvent(coords)
}

func (c *Controller) Cleanup() {
	c.jobRunner.Stop()

	for _, app := range c.apps {
		app.app.Cleanup()
	}
}
