# Cryptocurrency RGB Matrix Ticker 


![Crypto Ticker](/images/pictures/helium.png)

## Credits

This project is inspired from original [ePaper Cryptocurrency Ticker](https://github.com/veebch/btcticker) done by @veebch. So all credits are going to original project

I just replaced original e-Paper display by an RGB Matrix One. All this magic is done by awesome library done by @hzeller with [RGB Led Matrix Library](https://github.com/hzeller/rpi-rgb-led-matrix)


# Features

(supports all 7000+ coins/currencies listed on [CoinGecko](https://api.coingecko.com/api/v3/coins/list))

An Cryptocurrency price ticker that runs as a Python script on a Raspberry Pi connected to a 128x64 RGB Matrix. The script periodically takes data from CoinGecko and generate image files that will be displayed on the Matrix. Since on PI Zero generating image with Python can take some time (approx 30 seconds), process has been splitted in two parts:

- one thread fired on basis interval to get data from coingecko.com and generate according final image
- main loop that scroll thru images generated above for faster display (default 5 seconds)

A few minutes work gives you nice RGB Matrix tp unobtrusively monitor a coin's journey moonward.

## Crypto logo. 

If image file corresponding to name of crypto is found (ie `bitcoin_32.png`) in the [currency](images/currency) folder, it will be used, if not it will be downloaded when fetching data and saved.

Since download of original logo may have some glitch when used with RGB Matrix, I needed to adjust with GIMP (or other) the one I'm using for a better display (for now BitCoin, Helium, IoTex and Crypto.com). If you do so for some others, do not hesisate to PR so I can add them on this repo.

I've also included a script [get_icons.sh](get_icons.sh) go get crypto icons.

# Getting started

## Prerequisites

These instructions assume that your Raspberry Pi is already connected to the Internet, happily running `pip` and has `python3` installed)

If you are running the Pi headless, connect to your Raspberry Pi using `ssh`.

### RGB LED Matrix tools and driver

Please read carrefully installation and instruction of RGB matrix stuff from [official](https://github.com/hzeller/rpi-rgb-led-matrix) and test that your RGB matrix is working with officials [Python samples](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python).

No need to go futher is this does not works.

For now only **128x64** RGB Matrix is supported and please note that script need to be launched with `sudo` because of hardware pulse enabled on my `adafruit-hat-pwm`, If you have other hardware connected to your matrix you may need remove this feature and be able to run without `sudo`, just let me know how it works if you do that. You can change RGB hardware config in the main [cryptoticker.py](cryptoticker.py) file (and yes, it's hard coded for now)

### Install this repo

Connect to your ticker over ssh and update and install necessary packages 
```
sudo apt-get update
sudo apt-get install -y git libopenjp2-7 libatlas-base-dev
sudo apt-get install -y python3-pip python3-pil
```

Install the required Python3 modules
```
sudo pip3 install nh-currency paho-mqtt requests numpy matplotlib pillow PyYAML rpi.gpio
```

Now clone the required software 

```
cd ~
git clone https://github.com/hallard/rgb-matrix-crypto-ticker
```

Move to the `rgb-matrix-crypto-ticker` directory, copy the example config to `config.yaml`
```
cd rgb-matrix-crypto-ticker
cp config_example.yaml config.yaml
```

Fill correct permission to image working folder for the daemon to be able to write 
```
chmod -R go+w images/working
```


## Configuration via config file

The file `config.yaml` (the copy of `config_example.yaml` you made earlier) contains a number of options that may be tweaked:

```yaml
display:
  cycle: true
  updatefrequency: 5
  scroll: none
  scroll_pixel: 2
  brightness: 50
ticker:
  currency: bitcoin,crypto-com-chain,helium,iotex
  exchange: default
#  fiatcurrency: usd,eur,gbp
  fiatcurrency: eur
  sparklinedays: 1 
  updatefrequency: 60
mqtt:
  host: 192.168.1.8
  port: 1883
  topic: smartclock/smartclock-40e0/tele/SENSOR
```

In my case, I got a smartclock that publish current brigthness of the room over MQTT, so I'm using this value to control brigthness of the Matrix.
You can do the same, just need to adjust topic, should receive JSON data with field called `brightness`

```json
{
    "analog":47,
    "max_brightness":64,
    "min_brightness":8,
    "brightness":8,
    "light":46
}
```

### Values

- **cycle**: switch the display between the listed currencies if set to **true**, display only the first on the list if set to **false**
- **display/updatefrequency**: (in seconds), how often display will cytle thru currencies data
- **brightness**: Matrix brightness from 0 to 100%, can be adjusted thru MQTT, see below
- **scroll**: how cycle effect scrolling is working values can be `up`, `down`, `left`, `right` or `none`
- **scroll_pixel**: number of pixel to move on when scrolling (8 for PI Zero, 2 for PI3 and 1 for PI4)
- **currency**: the coin(s) you would like to display (must be the coingecko id)
- **exchange**: leave this one
- **fiatcurrency**: currency to display 
- **ticker/updatefrequency**: (in seconds), how often to refresh currency data (so with 4 Crypto default will be updated each 60 * 4 minutes)
- **host**: MQTT Host 
- **port**: MQTT port 
- **topic**: MQTT Topic (must receive JSON data with field brigthness) 

![Crypto Ticker Scrolling](/images/pictures/animated-scroll.gif)

## Test

Quick launch program before starting as a service
```
sudo ./cryptoticker.py
```

## Add Autostart

```
cat <<EOF | sudo tee /etc/systemd/system/cryptoticker.service
[Unit]
Description=cryptoticker
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u /home/pi/rgb-matrix-crypto-ticker/cryptoticker.py
WorkingDirectory=/home/pi/rgb-matrix-crypto-ticker/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF
```
Now, simply enable the service you just made and reboot
```  
sudo systemctl enable cryptoticker.service
sudo systemctl start cryptoticker.service

sudo reboot
```

# Contributing

To contribute, please fork the repository and use a feature branch. Pull requests are welcome.

# Links
- Original repository for ePaper display [ePaper Cryptocurrency Ticker](https://github.com/veebch/btcticker) 
- RGB Led Matrix for [Raspberry PI](https://github.com/hzeller/rpi-rgb-led-matrix)

# Licencing

GNU GENERAL PUBLIC LICENSE Version 3.0
