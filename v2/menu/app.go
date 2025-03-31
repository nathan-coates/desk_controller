package menu

import (
	"fmt"
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
	"time"
)

type mId int

const (
	base mId = iota
	refresh
	shutdown
	restart
)

type HookId int

const (
	Refresh HookId = iota
	Shutdown
	Restart
)

type MenuApp struct {
	pendingUpdateDisplay *shared.Result
	hooks                map[HookId]func()
	buttons              []*shared.AppButton
	currentId            mId
	previousId           mId
	locked               bool
}

func New() shared.App {
	app := &MenuApp{
		buttons: []*shared.AppButton{
			{ // Refresh
				HitBox: shared.HitBox{
					XStart: 33,
					XEnd:   88,
					YStart: 50,
					YEnd:   71,
				},
			},
			{ // Shutdown
				HitBox: shared.HitBox{
					XStart: 97,
					XEnd:   152,
					YStart: 50,
					YEnd:   71,
				},
			},
			{ // Restart
				HitBox: shared.HitBox{
					XStart: 161,
					XEnd:   216,
					YStart: 50,
					YEnd:   71,
				},
			},
		},
		pendingUpdateDisplay: nil,
		currentId:            base,
		previousId:           base,
		hooks:                make(map[HookId]func()),
	}

	app.buttons[0].Action = app.actionClosure(refresh)
	app.buttons[0].ImmediateAction = app.immediateActionClosure(refresh)

	app.buttons[1].Action = app.actionClosure(shutdown)
	app.buttons[1].ImmediateAction = app.immediateActionClosure(shutdown)

	app.buttons[2].Action = app.actionClosure(restart)
	app.buttons[2].ImmediateAction = app.immediateActionClosure(restart)

	return app
}

func (m *MenuApp) actionClosure(menuId mId) func() {
	return func() {
		defer func() {
			m.locked = false
		}()

		var err error
		switch menuId {
		case refresh:
			time.Sleep(3 * time.Second)
			fn, ok := m.hooks[Refresh]
			if ok {
				fn()
			}

			m.currentId = base

			result := shared.Pool.
				Get().(*shared.Result).
				Set(shared.Success, m.Display())

			m.pendingUpdateDisplay = result
			err = nil
		case shutdown:
			fmt.Println("shutdown")
			time.Sleep(3 * time.Second)
			fn, ok := m.hooks[Shutdown]
			if ok {
				fn()
			}

			err = nil
		case restart:
			fmt.Println("restart")
			time.Sleep(3 * time.Second)
			fn, ok := m.hooks[Restart]
			if ok {
				fn()
			}
			err = nil
		default:
			err = fmt.Errorf("unknown menu id %d", menuId)
		}

		if err != nil {
			log.Println(err)
			m.currentId = m.previousId

			result := shared.Pool.
				Get().(*shared.Result).
				Set(shared.Error, m.Error())

			m.pendingUpdateDisplay = result
			return
		}
	}
}

func (m *MenuApp) immediateActionClosure(menuId mId) func() {
	return func() {
		m.previousId = m.currentId
		m.currentId = menuId
	}
}

func (m *MenuApp) TouchEvent(event shared.TouchCoordinates) bool {
	for _, button := range m.buttons {
		if event.In(button.HitBox) {
			if !m.locked {
				m.locked = true
				button.ImmediateAction()
				go button.Action()
				return true
			}
			return false
		}
	}

	return false
}

func (m *MenuApp) Display() string {
	switch m.currentId {
	case base:
		return MenuBase
	case refresh:
		return MenuRefresh
	case shutdown:
		return MenuShutdown
	case restart:
		return MenuRestart
	default:
		return MenuBase
	}
}

func (m *MenuApp) Error() string {
	return m.Display()
}

func (m *MenuApp) PendingUpdate() *shared.Result {
	defer func() {
		if m.pendingUpdateDisplay != nil {
			m.pendingUpdateDisplay = nil
		}
	}()

	return m.pendingUpdateDisplay
}

func (m *MenuApp) PeriodicJob() (func(), time.Duration) {
	return nil, time.Duration(0)
}

func (m *MenuApp) Cleanup() {
}

func (m *MenuApp) RegisterHook(id int, hook func()) {
	m.hooks[HookId(id)] = hook
}
