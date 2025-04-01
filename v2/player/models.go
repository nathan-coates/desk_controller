package player

type ErrorResponseDetails struct {
	Message string `json:"message"`
	Status  int    `json:"status"`
}
type ErrorResponse struct {
	Error ErrorResponseDetails `json:"error"`
}

type PlaybackStateResponse struct {
	IsPlaying bool `json:"is_playing"`
}

type RefreshResponse struct {
	AccessToken  string `json:"access_token"`
	TokenType    string `json:"token_type"`
	RefreshToken string `json:"refresh_token"`
	Scope        string `json:"scope"`
	ExpiresIn    int    `json:"expires_in"`
}
