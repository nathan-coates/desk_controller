# Desk Controller

Waveshare + Zero project I made. It has three "apps" - KVM, Spotify, and Hue controllers. These are tailored to my personal setup.

This is "V1", I have a full Golang version I'm currently working on that will be "V2".

I took Waveshare's Python code from here: [https://github.com/waveshareteam/Touch_e-Paper_HAT/tree/main/python](https://github.com/waveshareteam/Touch_e-Paper_HAT/tree/main/python), making slight tweaks based on PyCharm's linting suggestions.

## Setup

### Hardware

* Raspberry Pi Zero 2 W
* Waveshare 2.13in Touch e-Paper HAT
* [PiBeam](https://github.com/sbcshop/PiBeam_Hardware)
* [Monoprice Blackbird 4K DisplayPort® 1.4 and USB 3.0 4x1 KVM Switch](https://www.amazon.com/dp/B093N1DR8Y)

### Software

* Copy `pibeam/main.py` file to PiBeam running the default MicroPython-based firmware
* Clone repo to Raspberry Pi Zero
* Create a `.env` file and fill in the values following `.env.sample`
* Using `uv` will handle dependencies for you

## Run

### Emulate

`uv run emulate.py`

### Production

`uv run main.py`
