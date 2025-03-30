package shared

import "sync"

var Pool = sync.Pool{
	New: func() interface{} {
		return &Result{}
	},
}
