package player

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
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
	clientId     string
	clientSecret string
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

	clientId := os.Getenv("SPOTIFY_CLIENT")
	if clientId == "" || clientId == "xxxx" {
		log.Fatal("Missing Spotify client id")
	}

	clientSecret := os.Getenv("SPOTIFY_CLIENT")
	if clientSecret == "" || clientSecret == "xxxx" {
		log.Fatal("Missing Spotify client secret")
	}

	c := &Client{
		accessToken:  accessToken,
		refreshToken: refreshToken,
		clientId:     clientId,
		clientSecret: clientSecret,
		deviceId:     deviceId,
		headers: map[string]string{
			"Authorization": "Bearer " + accessToken,
		},
		httpClient: &http.Client{
			Timeout: time.Second * 3,
		},
	}

	_, err := c.GetPlaybackState()
	if err != nil {
		log.Fatal(err)
	}

	return c
}

func (c *Client) buildHeader(r *http.Request) {
	for k, v := range c.headers {
		r.Header.Set(k, v)
	}
}

func (c *Client) GetPlaybackState() (bool, error) {
	req, err := http.NewRequest(
		"GET",
		UrlBase,
		nil,
	)
	if err != nil {
		log.Println(err)
		return false, err
	}

	c.buildHeader(req)

	res, err := c.httpClient.Do(req)
	if err != nil {
		log.Println(err)
		return false, err
	}

	defer res.Body.Close()

	switch res.StatusCode {
	case http.StatusOK:
		var data PlaybackStateResponse
		err = json.NewDecoder(res.Body).Decode(&data)
		if err != nil {
			log.Println(err)
			return false, err
		}

		if data.IsPlaying != c.Playing {
			c.Playing = !c.Playing
			return true, nil
		}
		return false, nil
	case http.StatusNoContent:
		if c.Playing {
			c.Playing = false
			return true, nil
		}
		return false, nil
	default:
		var data ErrorResponse
		err = json.NewDecoder(res.Body).Decode(&data)
		if err != nil {
			log.Println(err)
			return false, err
		}

		if data.Error.Message == AccessError {
			err = c.refresh()
			if err != nil {
				return false, err
			}
			return c.GetPlaybackState()
		}

		return false, err
	}
}

func (c *Client) playback(pause bool) error {
	url := UrlPlay
	if pause {
		url = UrlPause
	}

	req, err := http.NewRequest(
		"PUT",
		url,
		nil,
	)
	if err != nil {
		log.Println(err)
		return err
	}

	c.buildHeader(req)

	q := req.URL.Query()
	q.Set("deviceId", c.deviceId)
	req.URL.RawQuery = q.Encode()

	res, err := c.httpClient.Do(req)
	if err != nil {
		log.Println(err)
		return err
	}

	defer res.Body.Close()

	if res.StatusCode < 200 || res.StatusCode > 299 {
		var data ErrorResponse
		err = json.NewDecoder(res.Body).Decode(&data)
		if err != nil {
			log.Println(err)
			return err
		}

		if data.Error.Message == AccessError {
			err = c.refresh()
			if err != nil {
				return err
			}

			return c.playback(pause)
		}

		return err
	}

	c.Playing = !pause
	return nil
}

func (c *Client) Play() error {
	return c.playback(false)
}

func (c *Client) Pause() error {
	return c.playback(true)
}

func (c *Client) ChangeTrack(direction Direction) error {
	if !c.Playing {
		return nil
	}

	var changeUrl string
	switch direction {
	case NextDir:
		changeUrl = UrlNext
	case BackDir:
		changeUrl = UrlBack
	default:
		return fmt.Errorf("invalid direction: %d", direction)

	}

	req, err := http.NewRequest(
		"POST",
		changeUrl,
		nil,
	)
	if err != nil {
		log.Println(err)
		return err
	}

	c.buildHeader(req)

	q := req.URL.Query()
	q.Set("deviceId", c.deviceId)
	req.URL.RawQuery = q.Encode()

	res, err := c.httpClient.Do(req)
	if err != nil {
		log.Println(err)
		return err
	}

	defer res.Body.Close()

	if res.StatusCode != http.StatusNoContent {
		var data ErrorResponse
		err = json.NewDecoder(res.Body).Decode(&data)
		if err != nil {
			log.Println(err)
			return err
		}

		if data.Error.Message == AccessError {
			err = c.refresh()
			if err != nil {
				return err
			}
			return c.ChangeTrack(direction)
		}

		return err
	}

	return nil
}

func (c *Client) refresh() error {
	formData := url.Values{
		"grant_type":    {"refresh_token"},
		"refresh_token": {c.refreshToken},
		"client_id":     {c.deviceId},
	}

	req, err := http.NewRequest("POST", UrlAuth, strings.NewReader(formData.Encode()))
	if err != nil {
		log.Println(err)
		return err
	}

	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	req.SetBasicAuth(c.clientId, c.clientSecret)

	res, err := c.httpClient.Do(req)
	if err != nil {
		log.Println(err)
		return err
	}

	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		return errors.New("refresh failed")
	}

	var data RefreshResponse
	err = json.NewDecoder(res.Body).Decode(&data)
	if err != nil {
		log.Println(err)
		return err
	}

	c.accessToken = data.AccessToken
	c.headers["Authorization"] = "Bearer " + c.accessToken

	if data.RefreshToken != "" {
		c.refreshToken = data.RefreshToken
	}

	return updateEnvFile(c.refreshToken, c.accessToken)
}
