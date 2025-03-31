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
	Display string
	Result  ResultId
}

func (r *Result) Set(result ResultId, display string) *Result {
	r.Result = result
	r.Display = display
	return r
}

type AppButton struct {
	Action func()

	ImmediateAction func()
	HitBox          HitBox
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
