package player

import (
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
	"time"
)

type pId int

const (
	playing pId = iota
	paused
	next
	back
)

func (p pId) String() string {
	switch p {
	case playing:
		return "playing"
	case paused:
		return "paused"
	default:
		return "unknown"
	}
}

type HookId int

const (
	Playing HookId = iota
	Paused
	Next
	Back
)

func boolToPid(state bool) pId {
	if state {
		return playing
	}
	return paused
}

type PlayerApp struct {
	client               *Client
	pendingUpdateDisplay *shared.Result
	hooks                map[HookId]func()
	buttons              []*shared.AppButton
	currentId            pId
	directionButton      pId
	locked               bool
}

func New() shared.App {
	app := &PlayerApp{
		client: NewClient(),
		buttons: []*shared.AppButton{
			{ // Back
				HitBox: shared.HitBox{
					XStart: 16,
					XEnd:   63,
					YStart: 30,
					YEnd:   77,
				},
			},
			{ // Play/Pause
				HitBox: shared.HitBox{
					XStart: 101,
					XEnd:   148,
					YStart: 30,
					YEnd:   77,
				},
			},
			{ // Skip
				HitBox: shared.HitBox{
					XStart: 186,
					XEnd:   233,
					YStart: 30,
					YEnd:   77,
				},
			},
		},
		pendingUpdateDisplay: nil,
		currentId:            paused,
		directionButton:      paused,
		hooks:                make(map[HookId]func()),
	}

	app.buttons[0].Action = app.actionClosure(back)
	app.buttons[0].ImmediateAction = app.immediateActionClosure(back)

	app.buttons[1].Action = app.actionClosure(paused)
	app.buttons[1].ImmediateAction = app.immediateActionClosure(paused)

	app.buttons[2].Action = app.actionClosure(next)
	app.buttons[2].ImmediateAction = app.immediateActionClosure(next)

	app.currentId = boolToPid(app.client.Playing)

	return app
}

func (p *PlayerApp) actionClosure(playerId pId) func() {
	return func() {
		defer func() {
			p.locked = false
		}()

		var err error
		if playerId == paused {
			if p.currentId == playing {
				fn, ok := p.hooks[Paused]
				if ok {
					fn()
				}

				err = p.client.Pause()
			} else {
				fn, ok := p.hooks[Playing]
				if ok {
					fn()
				}
				err = p.client.Play()
			}
		} else {
			var hook HookId
			var direction Direction

			switch playerId {
			case next:
				hook = Next
				direction = NextDir
			case back:
				hook = Back
				direction = BackDir
			}

			time.Sleep(1 * time.Second)

			p.directionButton = playing
			result := shared.Pool.
				Get().(*shared.Result).
				Set(shared.Success, p.Display())

			p.pendingUpdateDisplay = result

			fn, ok := p.hooks[hook]
			if ok {
				fn()
			}

			err = p.client.ChangeTrack(direction)
		}
		if err != nil {
			if playerId == paused {
				if p.currentId == playing {
					p.currentId = paused
				} else {
					p.currentId = playing
				}
			}

			result := shared.Pool.
				Get().(*shared.Result).
				Set(shared.Error, p.Error())

			p.pendingUpdateDisplay = result
			return
		}
	}
}

func (p *PlayerApp) immediateActionClosure(playerId pId) func() {
	return func() {
		switch playerId {
		case paused:
			if p.currentId == playing {
				p.currentId = paused
			} else {
				p.currentId = playing
			}
		case next:
			p.directionButton = next
		case back:
			p.directionButton = back
		default:
			return
		}
	}
}

func (p *PlayerApp) TouchEvent(event shared.TouchCoordinates) bool {
	for _, button := range p.buttons {
		if event.In(button.HitBox) {
			if !p.locked {
				p.locked = true
				button.ImmediateAction()
				go button.Action()
				return true
			}
			return false
		}
	}

	return false
}

func (p *PlayerApp) Display() string {
	switch p.currentId {
	case playing:
		switch p.directionButton {
		case next:
			return PlayerPlayingNext
		case back:
			return PlayerPlayingBack
		default:
			return PlayerPlaying
		}
	case paused:
		return PlayerPaused
	default:
		return ""
	}
}

func (p *PlayerApp) Error() string {
	return PlayerError
}

func (p *PlayerApp) PendingUpdate() *shared.Result {
	defer func() {
		if p.pendingUpdateDisplay != nil {
			p.pendingUpdateDisplay = nil
		}
	}()

	return p.pendingUpdateDisplay
}

func (p *PlayerApp) PeriodicJob() (func(), time.Duration) {
	return func() {
		state, err := p.client.GetPlaybackState()
		if err != nil {
			log.Println(err)
		}

		p.currentId = boolToPid(state)
	}, 30 * time.Second
}

func (p *PlayerApp) Cleanup() {
	p.client.Pause()
}

func (p *PlayerApp) RegisterHook(id int, hook func()) {
	p.hooks[HookId(id)] = hook
}
