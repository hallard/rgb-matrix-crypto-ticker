[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

# Cryptocurrency RGB Matrix Ticker 

## Credits

### @veebch for btcticker
This project is inspired from original [ePaper Cryptocurrency Ticker](https://github.com/veebch/btcticker) done by @veebch. So all credits are going to original project

### @hzeller for RGB Matrix Code
I just replaced original e-Paper display by an RGB Matrix One. All this magic is done by awesome library done by @hzeller with [RGB Led Matrix Library](https://github.com/hzeller/rpi-rgb-led-matrix)


# Features

(supports all 7000+ coins/currencies listed on [CoinGecko](https://api.coingecko.com/api/v3/coins/list))

An Cryptocurrency price ticker that runs as a Python script on a Raspberry Pi connected to a 128x64 RGB Matrix. The script periodically takes data from CoinGecko and generate an final image file that will be displayed on the Matrix. Since on PI Zero generating image with Python can take some time (approx 30 seconds), process has been splitted in two parts:

- one thread fired on basis interval to get data from coingecko and generate according final image file saved to SD card
- main loop that scroll thru images generated above for faster display (default 5 seconds)

A few minutes work gives you a desk ornament that will tastefully and unobtrusively monitor a coin's journey moonward.

## Crypto logo. 

If image file corresponding to name of crypto is found (ie `btc_32.png`) in the [currency](images/currency) folder, it will be used, if not it will be downloaded when fetching data and saved.

Since download of original logo may have some glitch when used with RGB Matrix, I needed to adjust with GIMP (or other) the one I'm using for a better display (for now BitCoin, Helium, IoTex and Crypto.com). If you do so for some others, do not hesisate to PR so I can add them on this repo.

If've included a script [get_icons.sh](get_icons.sh) go get crypto icons.

![Action Shot](/images/actionshot/BasicLunar.jpg)

# Getting started

## Prerequisites

(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running `pip` and has `python3` installed)

If you are running the Pi headless, connect to your Raspberry Pi using `ssh`.

### RGB LED Matrix tools and driver

Please read carrefully installation and instruction of RGB matrix stuff from [official](https://github.com/hzeller/rpi-rgb-led-matrix) and test that your RGB matrix is working with [Python samples](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python).

No need to go futher is this does not works.

### Install this repo

Connect to your ticker over ssh and update and install necessary packages 
```
sudo apt-get update
sudo apt-get install -y python3-pip mc git libopenjp2-7
sudo apt-get install -y libatlas-base-dev python3-pil
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
Install the required Python3 modules
```
python3 -m pip install -r requirements.txt
```

## Configuration via config file

The file `config.yaml` (the copy of `config_example.yaml` you made earlier) contains a number of options that may be tweaked:

```yaml
display:
  cycle: true
  updatefrequency: 5
  scroll: none
ticker:
  currency: bitcoin,crypto-com-chain,helium,iotex
  exchange: default
#  fiatcurrency: usd,eur,gbp
  fiatcurrency: eur
  sparklinedays: 1 
  updatefrequency: 60
```

### Values

- **cycle**: switch the display between the listed currencies if set to **true**, display only the first on the list if set to **false**
- **display/updatefrequency**: (in seconds), how often display will cytle thru currencies data
- **scroll**: how cycle effect scrolling is working values can be `top`, `bottom`, `left`, `right` or `none` (need fast PI for correct effect)
- **currency**: the coin(s) you would like to display (must be the coingecko id)
- **exchange**: leave this one
- **fiatcurrency**: currency to display 
- **ticker/updatefrequency**: (in seconds), how often to refresh currency data (so with 4 Crypto default will be updated each 60 * 4 minutes)

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