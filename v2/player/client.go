package player

import (
	"log"
	"net/http"
	"os"
)

const (
	UrlBase     = "https://api.spotify.com/v1/me/player"
	UrlPlay     = "https://api.spotify.com/v1/me/player/play"
	UrlPause    = "https://api.spotify.com/v1/me/player/pause"
	UrlNext     = "https://api.spotify.com/v1/me/player/next"
	UrlBack     = "https://api.spotify.com/v1/me/player/previous"
	UrlAuth     = "https://accounts.spotify.com/api/token"
	AccessError = "access token has expired"
)

type Direction int

const (
	NextDir Direction = iota
	BackDir
)

type Client struct {
	headers      map[string]string
	accessToken  string
	refreshToken string
	deviceId     string
	Playing      bool
	httpClient   *http.Client
}

func NewClient() *Client {
	accessToken := os.Getenv("SPOTIFY_ACCESS_TOKEN")
	if accessToken == "" || accessToken == "xxxx" {
		log.Fatal("Missing Spotify access token")
	}

	refreshToken := os.Getenv("SPOTIFY_REFRESH_TOKEN")

	deviceId := os.Getenv("SPOTIFY_DEVICE_ID")
	if deviceId == "" || deviceId == "xxxx" {
		log.Fatal("Missing Spotify device id")
	}

	c := &Client{
		accessToken:  accessToken,
		refreshToken: refreshToken,
		deviceId:     deviceId,
		headers: map[string]string{
			"Authorization": "Bearer " + refreshToken,
		},
	}

	return c
}

func (c *Client) buildHeader(r *http.Request) {
	for k, v := range c.headers {
		r.Header.Set(k, v)
	}
}

func (c *Client) GetPlaybackState() (bool, error) {
	return false, nil
}

func (c *Client) Play() error {
	return nil
}

func (c *Client) Pause() error {
	return nil
}

func (c *Client) ChangeTrack(direction Direction) error {
	return nil
}

func (c *Client) refresh() error {
	return nil
}
