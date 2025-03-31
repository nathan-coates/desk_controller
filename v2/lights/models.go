package lights

type light struct {
	Id    string
	State bool
}

type GetGroupedLightResponse struct {
	On struct {
		On bool `json:"on"`
	} `json:"on"`
}

type HueResponse struct {
	Data []GetGroupedLightResponse `json:"data"`
}
