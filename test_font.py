#!/usr/bin/env python3
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
from PIL import BdfFontFile, FontFile
import os
import sys
import time
import textwrap
import decimal
import platform
import pathlib

if sys.platform != "darwin":
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.cols =128
    options.rows = 64
    #options.disable_hardware_pulsing = 1
    options.hardware_mapping = 'adafruit-hat-pwm'

    matrix = RGBMatrix(options = options)

dirname = os.path.dirname(__file__)
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
font_date = ImageFont.load(os.path.join(fontdir,'pil/5x8.pil'))

def place_text(img, text, x_offset=0, y_offset=0, fontsize=40, fontstring="ttf/Forum-Regular.ttf", fill='blue'):
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
        else:
            print("Not a valid font file {}".format(filenme))
            font = None
    except OSError:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', fontsize)

    if font != None:
        img_width, img_height = img.size
        text_width, _ = font.getsize(text)
        text_height = fontsize
        draw_x = (img_width - text_width)//2 + x_offset
        draw_y = (img_height - text_height)//2 + y_offset
        draw.text((draw_x, draw_y), text, font=font,fill=fill )

def writewrappedlines(img,text,fontsize=16,y_text=20,height=15, width=25,fontstring="ttf/Piboto-Bold.ttf", fill='blue'):
    lines = textwrap.wrap(text, width)
    numoflines=0
    for line in lines:
        place_text(img, line,0, y_text, fontsize,fontstring, fill)
        y_text += height
        numoflines+=1
    return img

def display_font(fontname, displayfrequency=5):
    timestamp= str(time.strftime("%d %b %Y %H:%M"))
    pricenowstring = "0.12345"
    symbolstring ="€"

    for font_size in range(20, 38):
        image = Image.new('RGBA', (128,64))
        draw = ImageDraw.Draw(image)
        timestamp= str(time.strftime("%d %b %Y %H:%M"))
        text = "{} Size {}".format(timestamp, font_size)
        draw.text((1,00),text,font =font_date,fill = 'lightskyblue')
        text = "{}".format(fontname)
        draw.text((1,10),text,font =font_date,fill = 'lightskyblue')

        # (img,text,fontsize=16,y_text=20,height=15,width=25
        #writewrappedlines(image, pricenowstring,19,15,19,10,"Piboto-Bold-19.bdf", fill=color )
        writewrappedlines(image, pricenowstring+symbolstring,font_size,0,font_size,15,fontname, fill='gold' )

        if sys.platform != "darwin":
            matrix.SetImage(image.convert('RGB'))
        time.sleep(displayfrequency)


def show_font(fontname, displayfrequency=5):
    global fontdir
    fontfile = os.path.join(fontdir + fontname)

    if os.path.isfile(fontfile):
        path = pathlib.PurePath(fontfile)
        short_name = os.path.join(path.parent.name, os.path.basename(fontfile))
        display_font(short_name)

    elif os.path.isdir(fontfile):
        for filename in os.listdir(fontfile):
            full_file = os.path.join(fontfile, filename)
            path = pathlib.PurePath(full_file)
            short_name = os.path.join(path.parent.name, os.path.basename(filename))

            print(short_name)
            # checking for a specific font if it is a file
            # if os.path.isfile(f) and filename == 'Roboto-Bold.ttf':
            # checking if it is a file
            if os.path.isfile(full_file):
                display_font(short_name)


def main():

    print('Starting...')
    show_font('/ttf/minisystem.ttf', 2)
    show_font('/googlefonts', 2)
    show_font('/ttf', 2)
    show_font('/pil', 2)

if __name__ == '__main__':
    main()
