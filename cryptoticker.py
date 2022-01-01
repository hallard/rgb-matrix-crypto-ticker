#!/usr/bin/env python3
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
from PIL import BdfFontFile, FontFile
import currency
import os
import subprocess
import platform
import sys
import logging
import time
import requests
import urllib, json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import yaml
import socket
import textwrap
import argparse
import decimal
import threading
import paho.mqtt.client as mqtt
import json


if sys.platform != "darwin":
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.cols =128
    options.rows = 64
    options.chain_length = 1
    options.parallel = 1
    #options.disable_hardware_pulsing = 1
    options.hardware_mapping = 'adafruit-hat-pwm'
    #options.hardware_mapping = 'regular'
    matrix = RGBMatrix(options = options)
else:
    import locale
    loc = locale.getlocale(locale.LC_ALL) 
    locale.setlocale(locale.LC_ALL, 'fr_FR')

dirname = os.path.dirname(__file__)
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.yaml')
#font_date = ImageFont.truetype(os.path.join(fontdir,'PixelSplitter-Bold.ttf'),8)
font_date = ImageFont.load(os.path.join(fontdir,'pil/5x8.pil'))
font_trend = ImageFont.load(os.path.join(fontdir,'pil/6x9.pil'))
font_error = ImageFont.load(os.path.join(fontdir,'pil/tom-thumb.pil'))


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

file_lock = threading.Lock()
previous_image = None
mqtt_topic = ""
brightness = 50

def on_mqtt_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    global mqtt_topic
    # Print result of connection attempt
    print("Connected with result code {0}".format(str(rc)))  
    # Subscribe to the topic to get ambiant brightness
    client.subscribe(mqtt_topic)  


def on_mqtt_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    global brightness
    #print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    try:
        d = json.loads(msg.payload)
        brightness = int(d['brightness']) * 2
        if brightness < 8:
            brightness = 8
        elif brightness > 100:
            brightness = 100
    except:
        pass

def internet(hostname="google.com"):
    """
    Host: google.com
    """
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except:
        logging.info("Google says No")
        time.sleep(1)
    return False

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def _place_text(img, text, x_offset=0, y_offset=0, fontsize=8, fontstring="pil/5x8.pil", fill='blue'):
    '''
    Put some centered text at a location on the image.
    '''
    draw = ImageDraw.Draw(img)
    try:
        filename = os.path.join(fontdir, fontstring)
        if fontstring.endswith(".ttf"):
            font = ImageFont.truetype(filename, fontsize)
        elif fontstring.endswith(".pil"):
            font = ImageFont.load(filename)
        elif fontstring.endswith(".bdf"):
            with open(filename, "rb") as bdf_file:
                font = BdfFontFile.BdfFontFile(bdf_file)
    except OSError:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', fontsize)
    img_width, img_height = img.size

    text_width, _ = font.getsize(text)
    text_height = fontsize
    draw_x = (img_width - text_width)//2 + x_offset
    draw_y = (img_height - text_height)//2 + y_offset
    draw.text((draw_x, draw_y), text, font=font,fill=fill )

def writewrappedlines(img,text,fontsize=8,y_text=0,height=8, width=26,fontstring="pil/5x8.pil", fill='blue'):
    lines = textwrap.wrap(text, width)
    numoflines=0
    for line in lines:
        _place_text(img, line,0, y_text, fontsize,fontstring, fill)
        y_text += height
        numoflines+=1
    return img

def getgecko(url):
    try:
        geckojson=requests.get(url, headers=headers).json()
        connectfail=False
    except requests.exceptions.RequestException as e:
        logging.error("Issue with CoinGecko")
        connectfail=True
        geckojson={}
    return geckojson, connectfail

def getData(config,other):
    """
    The function to grab the data (TO DO: need to test properly)
    """

    sleep_time = 10
    num_retries = 100
    whichcoin,fiat=configtocoinandfiat(config)
    logging.info("Getting Data")
    days_ago=int(config['ticker']['sparklinedays'])
    endtime = int(time.time())
    starttime = endtime - 60*60*24*days_ago
    starttimeseconds = starttime
    endtimeseconds = endtime
    geckourlhistorical = "https://api.coingecko.com/api/v3/coins/"+whichcoin+"/market_chart/range?vs_currency="+fiat+"&from="+str(starttimeseconds)+"&to="+str(endtimeseconds)
    logging.debug(geckourlhistorical)
    timeseriesstack = []
    for x in range(0, num_retries):
        rawtimeseries, connectfail=  getgecko(geckourlhistorical)
        if connectfail== True:
            pass
        else:
            logging.debug("Got price for the last "+str(days_ago)+" days from CoinGecko")
            timeseriesarray = rawtimeseries['prices']
            length=len (timeseriesarray)
            i=0
            while i < length:
                timeseriesstack.append(float (timeseriesarray[i][1]))
                i+=1
            # A little pause before hiting the api again
            time.sleep(1)
            # Get the price
        geckourl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency="+fiat+"&ids="+whichcoin
        logging.debug(geckourl)
        rawlivecoin , connectfail = getgecko(geckourl)
        if connectfail==True:
            pass
        else:
            logging.debug(rawlivecoin[0])
            liveprice = rawlivecoin[0]
            pricenow= float(liveprice['current_price'])
            other['symbol'] = liveprice['symbol']
            other['name'] = liveprice['name']
            alltimehigh = float(liveprice['ath'])
            # Quick workaround for error being thrown for obscure coins. TO DO: Examine further
            try:
                other['market_cap_rank'] = int(liveprice['market_cap_rank'])
            except:
                config['display']['showrank']=False
                other['market_cap_rank'] = 0
            other['volume'] = float(liveprice['total_volume'])
            timeseriesstack.append(pricenow)
            if pricenow>alltimehigh:
                other['ATH']=True
            else:
                other['ATH']=False

        if connectfail==True:
            message="Trying again in ", sleep_time, " seconds"
            logging.warn(message)
            time.sleep(sleep_time)  # wait before trying to fetch the data again
            sleep_time *= 2  # exponential backoff
        else:
            break
    return timeseriesstack, whichcoin

def beanaproblem(message):
    # A visual cue that the wheels have fallen off
    image = Image.new('RGBA', (128, 64))
    draw = ImageDraw.Draw(image)
    try: 
        thebean = Image.open(os.path.join(picdir,'thebean.bmp'))
        thebean= ImageOps.invert(thebean).resize((64,64))
        image.paste(thebean, (55,0))
    except:
        pass
    draw.text((1, 0),str(time.strftime("%d/%m/%y")), font=font_date, fill='magenta')
    draw.text((9,10),str(time.strftime("%H:%M")),    font=font_date, fill='magenta')
    writewrappedlines(image, "Issue:"+message, y_text=3, fill='red')
    logging.info(message)
    return image

def makeSpark(pricestack):
    # Draw and save the sparkline that represents historical data
    # Subtract the mean from the sparkline to make the mean appear on the plot (it's really the x axis)
    pricechangeraw = round((pricestack[-1]-pricestack[0])/pricestack[-1]*100,2)
    chartcolor = 'green' if pricechangeraw > 0 else 'red'

    themean= sum(pricestack)/float(len(pricestack))
    x = [xx - themean for xx in pricestack]
    plt.style.use('dark_background')
    fig, ax = plt.subplots(1,1,figsize=(12, 3.1))
    #fig, ax = plt.subplots(1,1,figsize=(px*90, px*32))
    plt.plot(x, color=chartcolor, linewidth=4)
    plt.plot(len(x)-1, x[-1], color='yellow', marker='o')
    # Remove the Y axis
    for k,v in ax.spines.items():
        v.set_visible(False)
    ax.set_facecolor('black')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axhline(c='blue', linewidth=3, linestyle=(0, (5, 2, 1, 2)))
    # Save the resulting file to the images directory (BMP not supported)
    plt.savefig(os.path.join(picdir,'working/spark.png'), dpi=10, pad_inches=0)
    plt.close(fig)
    plt.cla() # Close plot to prevent memory error
    ax.cla() # Close axis to prevent memory error
    #imgspk = Image.open(os.path.join(picdir,'spark.png'))
    #file_out = os.path.join(picdir,'spark.bmp')
    #imgspk.save(file_out)
    #imgspk.close()
    return

def updateImage(config,pricestack,other):
    """
    Takes the price data, the desired coin/fiat combo along with the config info for formatting
    if config is re-written following adustment we could avoid passing the last two arguments as
    they will just be the first two items of their string in config
    """
    with open(configfile) as f:
        originalconfig = yaml.load(f, Loader=yaml.FullLoader)
    originalcoin=originalconfig['ticker']['currency']
    originalcoin_list = originalcoin.split(",")
    originalcoin_list = [x.strip(' ') for x in originalcoin_list]
    whichcoin,fiat=configtocoinandfiat(config)
    days_ago=int(config['ticker']['sparklinedays'])
    symbolstring=currency.symbol(fiat.upper())
    if fiat=="jpy" or fiat=="cny":
        symbolstring="¥"
    pricenow = pricestack[-1]

#    currencythumbnail= 'currency/'+whichcoin+'.bmp'
    currencythumbnail= 'currency/'+whichcoin+'_32.png'
    tokenfilename = os.path.join(picdir,currencythumbnail)
    sparkbitmap = Image.open(os.path.join(picdir,'working/spark.png'))
    #sparkbitmap.thumbnail((90,27))

#   Check for token image, if there isn't one, get on off coingecko, resize it and pop it on a white background
    if os.path.isfile(tokenfilename):
        logging.debug("Getting token Image from Image directory")
        logging.info(tokenfilename)
        tokenimage = Image.open(tokenfilename).convert("RGBA")
    else:
        tokenimageurl = "https://api.coingecko.com/api/v3/coins/"+whichcoin+"?tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false"
        logging.debug("Getting token Image from Coingecko")
        logging.info(tokenimageurl)
        rawimage = requests.get(tokenimageurl, headers=headers).json()
        tokenimage = Image.open(requests.get(rawimage['image']['large'], headers = headers, stream=True).raw).convert("RGBA")
        tokenimage.thumbnail((32,32), Image.ANTIALIAS)

    tokenimage.save(os.path.join(picdir,'working/token.bmp'))
    pricechangeraw = round((pricestack[-1]-pricestack[0])/pricestack[-1]*100,2)
    if pricechangeraw >= 10:
        pricechange = str("%+.1f" % pricechangeraw)+"%"
    elif pricechangeraw <= -10:
        pricechange = str("%.1f" % pricechangeraw)+"%"
    else:
        pricechange = str("%+.2f" % pricechangeraw)+"%"

    color = 'red' if pricechangeraw < 0 else 'green'

    #pricenow_size = 31 #pricenow_font = "ttf/Piboto-Bold.ttf"
    #pricenow_size = 28/30 #pricenow_font = "googlefonts/Roboto-Regular.ttf"
    #pricenow_size = 28 pricenow_font = "googlefonts/Roboto-Bold.ttf"
    #pricenow_size = 30 pricenow_font = "googlefonts/Roboto-Medium.ttf"

    pricenow_size = 30
    pricenow_font = "googlefonts/Roboto-Bold.ttf"
    pricenow_offset = 18

    # #of digit after decimal point
    d = abs (decimal.Decimal(str(pricenow)).as_tuple().exponent)
    if pricenow > 1000:
        pricenowstring =str(format(int(pricenow),""))
    elif pricenow >= 1:
        if d>3: d=3
        fmtstr = ":.{}f".format(d)
        fmtstr = "{"+fmtstr+"}"
        pricenowstring = fmtstr.format(pricenow)
    else:
        if d>5: d=5
        fmtstr = ":.{}f".format(d)
        fmtstr = "{"+fmtstr+"}"
        pricenowstring = fmtstr.format(pricenow)

    # Create final image
    image = Image.new('RGBA', (128,64))
    draw = ImageDraw.Draw(image)
    # First place spark because it has big border, don't want to override image
    image.paste(sparkbitmap,(20,5))
    # Place date / time
    draw.text((42,0), str(time.strftime("%d %b %Y %H:%M")), font=font_date, fill='sandybrown')
    # Coin icon 
    image.paste(tokenimage, (0,0))
    # Place coin name + Price change
    draw.text((1,32),other['name'],font =font_date,fill = 'lightskyblue')
    draw.text((90,32),pricechange,font =font_trend,fill = color)

    # Big font price placing
    # (img,text,fontsize=16,y_text=20,height=15,width=25
    writewrappedlines(image, pricenowstring+symbolstring, pricenow_size, pricenow_offset, pricenow_size, 15, pricenow_font, 'gold')

    imgfile = os.path.join(picdir, 'working/' + whichcoin+'.png')
    logging.info("Saving " + imgfile)

    # Securly save file in case main thread locked the file on display
    while file_lock.locked():
        time.sleep(0.1)
    file_lock.acquire()
    image.save(imgfile)
    file_lock.release()

    # Return the ticker image
    return image

def currencystringtolist(currstring):
    # Takes the string for currencies in the config.yaml file and turns it into a list
    curr_list = currstring.split(",")
    curr_list = [x.strip(' ') for x in curr_list]
    return curr_list

def currencycycle(curr_string):
    curr_list=currencystringtolist(curr_string)
    # Rotate the array of currencies from config.... [a b c] becomes [b c a]
    curr_list = curr_list[1:]+curr_list[:1]
    return curr_list

def display_image(img, imgfile=None, scroll=None, scroll_pixel=2):
    global previous_image
    global brightness
    # Make image fit our screen.
    #img.thumbnail((128, 64), Image.ANTIALIAS)
    if sys.platform != "darwin":

        img = img.convert('RGB')
        matrix.brightness = brightness

        if scroll==None or scroll=='none':
            matrix.SetImage(img.convert('RGB'))
        else:
            double_buffer = matrix.CreateFrameCanvas()
            img_width, img_height = img.size

            if scroll == 'down':
                ypos = 0
                while ypos < img_height:
                    ypos += scroll_pixel
                    if previous_image != None:
                        double_buffer.SetImage(previous_image, 0, -ypos)
                    double_buffer.SetImage(img, 0, -ypos + img_height)
                    double_buffer = matrix.SwapOnVSync(double_buffer)
                    # Use this if it's scrolling too fast
                    #time.sleep(0.01)

            elif scroll == 'up':
                ypos = 0
                while ypos < img_height:
                    ypos += scroll_pixel
                    if previous_image != None:
                        double_buffer.SetImage(previous_image, 0, ypos)
                    double_buffer.SetImage(img, 0, ypos - img_height)
                    double_buffer = matrix.SwapOnVSync(double_buffer)
                    # Use this if it's scrolling too fast
                    #time.sleep(0.01)

            elif scroll == 'left':
                xpos = 0
                while xpos < img_width:
                    xpos += scroll_pixel * 2
                    if previous_image != None:
                        double_buffer.SetImage(previous_image, -xpos)
                    double_buffer.SetImage(img, -xpos + img_width)
                    double_buffer = matrix.SwapOnVSync(double_buffer)
                    # Use this if it's scrolling too fast
                    #time.sleep(0.01)

            elif scroll == 'right':
                xpos = 0
                while xpos < img_width:
                    xpos += scroll_pixel * 2
                    if previous_image != None:
                        double_buffer.SetImage(previous_image, xpos)
                    double_buffer.SetImage(img, xpos - img_width)
                    double_buffer = matrix.SwapOnVSync(double_buffer)
                    # Use this if it's scrolling too fast
                    #time.sleep(0.01)

            # save current image for next scroll
            previous_image = img
    else:
        if imgfile != None:
            # For testing mon my mac 
            p = os.system("cp " + imgfile + " /Users/charles/ssh/zero-a2ee/rgb-matrix-crypto-ticker/images/working/")
            print(p) 
    return

def display_file(imgfile, scroll=None, scroll_pixel=2):
    global brightness
    if os.path.isfile(imgfile):
        logging.info("Displaying " + imgfile + " brightness:" + str(brightness))
    
        # just in case thread creating image working on this file
        while file_lock.locked():
            time.sleep(0.1)

        file_lock.acquire()
        img = Image.open(imgfile)
        file_lock.release()

        display_image(img, imgfile, scroll, scroll_pixel)
    else:
        logging.info("Can't display, file not found " + imgfile)

def fullupdate(config,lastcoinfetch):
    """
    The steps required for a full update of a specific coin
    it does not change the display, just prepare the image
    to be displayed
    """
    other={}
    try:
        # Get data 
        pricestack, whichcoin = getData(config, other)
        # generate sparkline
        makeSpark(pricestack)
        # update image for tuture display
        image=updateImage(config, pricestack, other)
        lastgrab=time.time()
        time.sleep(0.2)
    except Exception as e:
        message="Data pull/print problem"
        image=beanaproblem(str(e)+" Line: "+str(e.__traceback__.tb_lineno))
        display_image(image)
        time.sleep(20)
        lastgrab=lastcoinfetch
    return lastgrab

def configtocoinandfiat(config):
    crypto_list = currencystringtolist(config['ticker']['currency'])
    fiat_list=currencystringtolist(config['ticker']['fiatcurrency'])
    currency=crypto_list[0]
    fiat=fiat_list[0]
    return currency, fiat

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='info', help='Set the log level (default: info)')
    args = parser.parse_args()

    loglevel = getattr(logging, args.log.upper(), logging.WARN)
    logging.basicConfig(level=loglevel)

    # Testing problem error display
    #display_image(beanaproblem("The quick brown fox jumps over the lazy dog The quick brown fox jumps over the lazy dog"))
    #time.sleep(60)

    try:
        logging.info("Crypto Ticker")
        # Get the configuration from config.yaml
        with open(configfile) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        logging.info(config)
        
        staticcoins=config['ticker']['currency']
        # Note how many coins in original config file
        howmanycoins=len(config['ticker']['currency'].split(","))
        # Note that there has been no data pull yet
        datapulled=False
        # Time of start
        lastcoinfetch = time.time()
        # Quick Sanity check on update frequency (when data value are pulled from WEB)
        updatefrequency=float(config['ticker']['updatefrequency'])
        if updatefrequency < 60.0:
            updatefrequency=60.0
            logging.info("Throttling update frequency to 60 seconds")

        # Quick Sanity check on display cycle time
        displayfrequency=float(config['display']['updatefrequency'])
        if displayfrequency <2:
            displayfrequency=2.0
            logging.info("Throttling display frequency to 2 seconds")

        while internet() == False:
            logging.info("Waiting for internet")

        if config['mqtt']['host'] != None:
            global mqtt_topic
            # Create instance of client with client ID 
            mqtt_client = mqtt.Client("crypto_ticker_" + socket.gethostname())  
            mqtt_client.on_connect = on_mqtt_connect  # Define callback function for successful connection
            mqtt_client.on_message = on_mqtt_message  # Define callback function for receipt of a message
            mqtt_client.connect(config['mqtt']['host'], config['mqtt']['port'])
            mqtt_topic = config['mqtt']['topic']


        config['display']['currency'] = config['ticker']['currency']
        lastdisplay=time.time()-displayfrequency
        lastcoinfetch=time.time() - updatefrequency -1
        while True:
            if (time.time() - lastcoinfetch > updatefrequency) or (datapulled==False):
                if config['display']['cycle']==True:
                    crypto_list = currencycycle(config['ticker']['currency'])
                    config['ticker']['currency']=",".join(crypto_list)

                    # Create a thread from a function with arguments
                    th = threading.Thread(target=fullupdate, args=(config,lastcoinfetch))
                    # Start the thread
                    th.start()
                    lastcoinfetch=time.time()

                    #lastcoinfetch=fullupdate(config,lastcoinfetch)
                    datapulled = True

            if time.time() - lastdisplay > displayfrequency:
                crypto_list = currencycycle(config['display']['currency'])
                config['display']['currency']=",".join(crypto_list)
                crypto_list = currencystringtolist(config['display']['currency'])
                imgfile = os.path.join(picdir+'/working', crypto_list[0]+'.png')
                display_file(imgfile, config['display']['scroll'],config['display']['scroll_pixel'] )
                lastdisplay=time.time()

            # Reduces CPU load during that while loop
            if config['mqtt']['host'] != None:
                # do MQTT Stuff
                mqtt_client.loop()  

            time.sleep(0.01)
    except IOError as e:
        logging.error(e)
        image=beanaproblem(str(e)+" Line: "+str(e.__traceback__.tb_lineno))
        display_image(image)
    except Exception as e:
        logging.error(e)
        image=beanaproblem(str(e)+" Line: "+str(e.__traceback__.tb_lineno))
        display_image(image)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        image=beanaproblem("Keyboard Interrupt")
        display_image(image)
        exit()

if __name__ == '__main__':
    main()
