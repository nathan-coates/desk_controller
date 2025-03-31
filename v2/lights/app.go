package lights

import (
	"fmt"
	"github.com/elliotchance/orderedmap/v3"
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
	"strings"
	"time"
)

type lId int

const (
	d lId = iota
	lv
	b
)

func (l lId) String() string {
	switch l {
	case d:
		return "Den"
	case lv:
		return "Living Room"
	case b:
		return "Bedroom"
	default:
		return "unknown"
	}
}

type HookId int

const (
	D HookId = iota
	Lv
	B
)

type LightApp struct {
	client               *Client
	pendingUpdateDisplay *shared.Result
	idState              *orderedmap.OrderedMap[lId, bool]
	hooks                map[HookId]func()
	buttons              []*shared.AppButton
	locked               bool
}

func New() shared.App {
	app := &LightApp{
		client: NewClient(),
		buttons: []*shared.AppButton{
			{ // Den
				HitBox: shared.HitBox{
					XStart: 16,
					XEnd:   63,
					YStart: 30,
					YEnd:   77,
				},
			},
			{ // Living Room
				HitBox: shared.HitBox{
					XStart: 101,
					XEnd:   148,
					YStart: 30,
					YEnd:   77,
				},
			},
			{ // Bedroom
				HitBox: shared.HitBox{
					XStart: 186,
					XEnd:   233,
					YStart: 30,
					YEnd:   77,
				},
			},
		},
		pendingUpdateDisplay: nil,
		hooks:                make(map[HookId]func()),
	}

	app.idState = orderedmap.NewOrderedMapWithElements[lId, bool](
		&orderedmap.Element[lId, bool]{
			Key:   d,
			Value: app.client.Lights[d].State,
		},
		&orderedmap.Element[lId, bool]{
			Key:   lv,
			Value: app.client.Lights[lv].State,
		},
		&orderedmap.Element[lId, bool]{
			Key:   b,
			Value: app.client.Lights[b].State,
		})

	app.buttons[0].Action = app.actionClosure(d)
	app.buttons[0].ImmediateAction = app.immediateActionClosure(d)

	app.buttons[1].Action = app.actionClosure(lv)
	app.buttons[1].ImmediateAction = app.immediateActionClosure(lv)

	app.buttons[2].Action = app.actionClosure(b)
	app.buttons[2].ImmediateAction = app.immediateActionClosure(b)

	return app
}

func (l *LightApp) actionClosure(lightId lId) func() {
	return func() {
		defer func() {
			l.locked = false
		}()

		current, _ := l.idState.Get(lightId)
		log.Printf("flipState %s from %v to %v", lightId, !current, current)

		var hook HookId

		switch lightId {
		case d:
			hook = D
		case lv:
			hook = Lv
		case b:
			hook = B
		}

		fn, ok := l.hooks[hook]
		if ok {
			fn()
		}

		err := l.client.ToggleGroupedLights(lightId)
		if err != nil {
			log.Println(err)
			l.idState.Set(lightId, !current)

			result := shared.Pool.
				Get().(*shared.Result).
				Set(shared.Error, l.Error())

			l.pendingUpdateDisplay = result
			return
		}
	}
}

func (l *LightApp) immediateActionClosure(lightId lId) func() {
	return func() {
		current, _ := l.idState.Get(lightId)
		l.idState.Set(lightId, !current)
	}
}

func (l *LightApp) TouchEvent(event shared.TouchCoordinates) bool {
	for _, button := range l.buttons {
		if event.In(button.HitBox) {
			if !l.locked {
				l.locked = true
				button.ImmediateAction()
				go button.Action()
				return true
			}
			return false
		}
	}

	return false
}

func (l *LightApp) Display() string {
	builder := strings.Builder{}

	for k, v := range l.idState.AllFromFront() {
		var light string
		switch k {
		case d:
			light = "d"
		case lv:
			light = "lv"
		case b:
			light = "b"

		}
		builder.WriteString(fmt.Sprintf("%s%t_", light, v))
	}

	final := builder.String()

	switch final {
	case "dfalse_lvfalse_bfalse_":
		return LightsdFLvFbdF
	case "dfalse_lvfalse_btrue_":
		return LightsdFLvFbdO
	case "dfalse_lvtrue_bfalse_":
		return LightsdFLvObdF
	case "dfalse_lvtrue_btrue_":
		return LightsdFLvObdO
	case "dtrue_lvfalse_bfalse_":
		return LightsdOLvFbdF
	case "dtrue_lvfalse_btrue_":
		return LightsdOLvFbdO
	case "dtrue_lvtrue_bfalse_":
		return LightsdOLvObdF
	case "dtrue_lvtrue_btrue_":
		return LightsdOLvObdO
	default:
		return LightsError
	}
}

func (l *LightApp) Error() string {
	return LightsError
}

func (l *LightApp) PendingUpdate() *shared.Result {
	defer func() {
		if l.pendingUpdateDisplay != nil {
			l.pendingUpdateDisplay = nil
		}
	}()

	return l.pendingUpdateDisplay
}

func (l *LightApp) PeriodicJob() (func(), time.Duration) {
	return func() {
		log.Println("Polling for light state")
		update := l.client.GetGroupedLightsState()
		if update {
			log.Println("There was an external change in light state")

			for i, v := range l.client.Lights {
				localState, _ := l.idState.Get(lId(i))
				if v.State != localState {
					l.idState.Set(lId(i), v.State)
				}
			}

			result := shared.Pool.
				Get().(*shared.Result).
				Set(shared.Success, l.Display())

			l.pendingUpdateDisplay = result
		}
	}, time.Duration(60) * time.Second
}

func (l *LightApp) Cleanup() {
}

func (l *LightApp) RegisterHook(id int, hook func()) {
	l.hooks[HookId(id)] = hook
}
