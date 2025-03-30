package shared

import "time"

type ResultId int

const (
	Error ResultId = iota
	Success
	Refresh
	Shutdown
	Restart
)

type Result struct {
	Result  ResultId
	Display string
}

func (r *Result) Set(result ResultId, display string) *Result {
	r.Result = result
	r.Display = display
	return r
}

type AppButton struct {
	HitBox HitBox

	Action func()

	ImmediateAction func()
}

type App interface {
	TouchEvent(TouchCoordinates) bool

	Display() string

	Error() string

	PendingUpdate() *Result

	PeriodicJob() (func(), time.Duration)

	Cleanup()

	RegisterHook(id int, hook func())
}
