package kvm

import (
	"embed"
	"github.com/nathan-coates/desk_controller/v2/shared"
	"log"
)

//go:embed *.bmp
var images embed.FS

var (
	KvmDesktop string
	KvmMacMini string
	KvmWorkMac string
	KvmError   string
)

func init() {
	mapping, err := shared.WriteImagesToFile(images)
	if err != nil {
		log.Fatal(err)
	}

	KvmDesktop = mapping["KVM_desktop.bmp"]
	KvmMacMini = mapping["KVM_mac_mini.bmp"]
	KvmWorkMac = mapping["KVM_work_mac.bmp"]
	KvmError = mapping["Error_kvm.bmp"]
}
