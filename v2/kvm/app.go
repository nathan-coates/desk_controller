package kvm

import (
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
	"time"
)

type cId int

const (
	macMini cId = iota
	workMac
	desktop
)

func (c cId) String() string {
	switch c {
	case macMini:
		return "Mac Mini"
	case workMac:
		return "Work Mac"
	case desktop:
		return "Desktop"
	default:
		return "unknown"
	}
}

type HookId int

const (
	MacMini HookId = iota
	WorkMac
	Desktop
)

type KvmApp struct {
	client               *Client
	pendingUpdateDisplay *shared.Result
	hooks                map[HookId]func()
	buttons              []*shared.AppButton
	currentId            cId
	previousId           cId
	locked               bool
}

func New() shared.App {
	app := &KvmApp{
		client: NewClient(),
		buttons: []*shared.AppButton{
			{ // Mac Mini
				HitBox: shared.HitBox{
					XStart: 16,
					XEnd:   63,
					YStart: 30,
					YEnd:   77,
				},
			},
			{ // Work Mac
				HitBox: shared.HitBox{
					XStart: 101,
					XEnd:   148,
					YStart: 30,
					YEnd:   77,
				},
			},
			{ // Desktop
				HitBox: shared.HitBox{
					XStart: 186,
					XEnd:   233,
					YStart: 30,
					YEnd:   77,
				},
			},
		},
		pendingUpdateDisplay: nil,
		currentId:            macMini,
		previousId:           macMini,
		hooks:                make(map[HookId]func()),
	}

	app.buttons[0].Action = app.actionClosure(macMini)
	app.buttons[0].ImmediateAction = app.immediateActionClosure(macMini)

	app.buttons[1].Action = app.actionClosure(workMac)
	app.buttons[1].ImmediateAction = app.immediateActionClosure(workMac)

	app.buttons[2].Action = app.actionClosure(desktop)
	app.buttons[2].ImmediateAction = app.immediateActionClosure(desktop)

	return app
}

func (k *KvmApp) actionClosure(computerId cId) func() {
	return func() {
		defer func() {
			k.locked = false
		}()

		log.Println("Switching to " + computerId.String())

		var hook HookId
		var command string

		switch computerId {
		case macMini:
			hook = MacMini
			command = "COMMAND_1"
		case workMac:
			hook = WorkMac
			command = "COMMAND_2"
		case desktop:
			hook = Desktop
			command = "COMMAND_3"
		}

		if k.previousId != computerId {
			fn, ok := k.hooks[hook]
			if ok {
				fn()
			}
		}

		err := k.client.SendCommand(command)
		if err != nil {
			k.currentId = k.previousId

			result := shared.Pool.
				Get().(*shared.Result).
				Set(shared.Error, k.Error())

			k.pendingUpdateDisplay = result
			return
		}
	}
}

func (k *KvmApp) immediateActionClosure(computerId cId) func() {
	return func() {
		k.previousId = k.currentId
		k.currentId = computerId
	}
}

func (k *KvmApp) TouchEvent(event shared.TouchCoordinates) bool {
	for _, button := range k.buttons {
		if event.In(button.HitBox) {
			if !k.locked {
				k.locked = true
				button.ImmediateAction()
				go button.Action()
				return true
			}
			return false
		}
	}

	return false
}

func (k *KvmApp) Display() string {
	switch k.currentId {
	case macMini:
		return KvmMacMini
	case workMac:
		return KvmWorkMac
	case desktop:
		return KvmDesktop
	default:
		return KvmMacMini
	}
}

func (k *KvmApp) Error() string {
	return KvmError
}

func (k *KvmApp) PendingUpdate() *shared.Result {
	defer func() {
		if k.pendingUpdateDisplay != nil {
			k.pendingUpdateDisplay = nil
		}
	}()

	return k.pendingUpdateDisplay
}

func (k *KvmApp) PeriodicJob() (func(), time.Duration) {
	return nil, time.Duration(0)
}

func (k *KvmApp) Cleanup() {
}

func (k *KvmApp) RegisterHook(id int, hook func()) {
	k.hooks[HookId(id)] = hook
}
