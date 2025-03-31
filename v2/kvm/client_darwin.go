//go:build darwin

package kvm

import (
	"go.bug.st/serial"
	"os"
	"time"
)

type Client struct {
	SerialMode *serial.Mode
	UsbAddress string
}

func NewClient() *Client {
	usbAddr := os.Getenv("KVM_USB_ADDR")

	mode := &serial.Mode{
		BaudRate: 115200,
		Parity:   serial.NoParity,
		DataBits: 8,
		StopBits: serial.OneStopBit,
	}

	return &Client{
		UsbAddress: usbAddr,
		SerialMode: mode,
	}
}

func (c *Client) SendCommand(command string) error {
	time.Sleep(500 * time.Millisecond)
	return nil
}
