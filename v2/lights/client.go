package lights

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

const UrlBase = "https://%s/clip/v2/resource"
const ApiEndpoint = "grouped_light"

type Client struct {
	headers      map[string]string
	url          string
	Lights       []light
	httpClient   *http.Client
	toggleBodies [2][]byte
}

func NewClient() *Client {
	hueIp := os.Getenv("HUE_IP")
	if hueIp == "" || hueIp == "xxxx" {
		log.Fatal("Missing Hue IP")
	}

	hueUsername := os.Getenv("HUE_USERNAME")
	if hueUsername == "" || hueUsername == "xxxx" {
		log.Fatal("Missing Hue Username")
	}

	hueLights := os.Getenv("HUE_LIGHTS")
	if hueLights == "" || hueLights == "xxxx" {
		log.Fatal("Missing Hue Lights")
	}

	c := &Client{
		url: fmt.Sprintf(UrlBase, hueIp),
		headers: map[string]string{
			"hue-application-key": hueUsername,
			"Content-Type":        "application/json",
		},
		Lights: make([]light, 3),
		httpClient: &http.Client{
			Timeout: time.Second * 3,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
		toggleBodies: [2][]byte{
			[]byte(`{"on":{"on": false}}`),
			[]byte(`{"on":{"on": true}}`),
		},
	}

	lightsStr := strings.Split(hueLights, ",")
	for i, l := range lightsStr {
		c.Lights[i] = light{
			Id:    l,
			State: false,
		}
	}

	c.GetGroupedLightsState()
	fmt.Println(c.Lights)

	return c
}

func (c *Client) buildUrl(id ...string) string {
	builder := strings.Builder{}

	builder.WriteString(c.url)
	builder.WriteString("/")
	builder.WriteString(ApiEndpoint)

	if len(id) > 0 {
		builder.WriteString("/")
		builder.WriteString(id[0])
	}

	return builder.String()
}

func (c *Client) buildHeader(r *http.Request) {
	for k, v := range c.headers {
		r.Header.Set(k, v)
	}
}

func (c *Client) ToggleGroupedLights(index lId) error {
	var toggleBodyIndex int
	if !c.Lights[index].State {
		toggleBodyIndex = 1
	}

	req, err := http.NewRequest(
		"PUT",
		c.buildUrl(c.Lights[index].Id),
		bytes.NewBuffer(c.toggleBodies[toggleBodyIndex]),
	)
	if err != nil {
		return nil
	}

	c.buildHeader(req)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return errors.New(resp.Status)
	}

	c.Lights[index].State = !c.Lights[index].State
	return nil
}

func (c *Client) GetGroupedLightsState() bool {
	var wg sync.WaitGroup
	var needUpdate atomic.Uint64

	for i := range c.Lights {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()

			req, err := http.NewRequest(
				"GET",
				c.buildUrl(c.Lights[index].Id),
				nil,
			)
			if err != nil {
				log.Println(err)
				return
			}

			c.buildHeader(req)

			res, err := c.httpClient.Do(req)
			if err != nil {
				log.Println(err)
				return
			}

			if res.StatusCode != http.StatusOK {
				log.Println(res.Status)
				return
			}

			defer res.Body.Close()

			respBody, err := io.ReadAll(res.Body)
			if err != nil {
				log.Println(err)
				return
			}

			var data HueResponse
			err = json.Unmarshal(respBody, &data)
			if err != nil {
				log.Println(err)
				return
			}

			state := data.Data[0].On.On

			savedState := c.Lights[index].State
			if savedState != state {
				c.Lights[index].State = state
				needUpdate.Add(1)
			}
		}(i)
	}
	wg.Wait()

	if int(needUpdate.Load()) > 0 {
		return true
	}
	return false
}
