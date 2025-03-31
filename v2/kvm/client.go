//go:build !darwin

package kvm

import (
	"go.bug.st/serial"
	"os"
	"time"
)

type Client struct {
	UsbAddress string
	SerialMode *serial.Mode
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
	port, err := serial.Open(c.UsbAddress, c.SerialMode)
	if err != nil {
		return err
	}
	defer port.Close()

	_, err = port.Write([]byte(command + "\n"))
	if err != nil {
		return err
	}

	time.Sleep(500 * time.Millisecond)
	return nil
}
