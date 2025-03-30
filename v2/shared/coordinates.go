package shared

type HitBox struct {
	XStart int
	XEnd   int
	YStart int
	YEnd   int
}

type TouchCoordinates struct {
	X int
	Y int
	S int
}

func NewTouchCoordinates(x, y, s int) TouchCoordinates {
	return TouchCoordinates{
		X: x,
		Y: y,
		S: s,
	}
}

func (c TouchCoordinates) In(hb HitBox) bool {
	if c.X < hb.XStart || c.X > hb.XEnd {
		return false
	}
	if c.Y < hb.YStart || c.Y > hb.YEnd {
		return false
	}
	return true
}
