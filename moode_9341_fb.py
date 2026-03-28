#!/usr/bin/python3
#
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageStat, ImageColor
from framebuffer import Framebuffer  # pytorinox
import subprocess
import time
import musicpd
import os
import os.path
from os import path
import RPi.GPIO as GPIO
#from gpiozero import Button
from mediafile import MediaFile
import requests
from io import BytesIO
import math
from numpy import mean
import yaml
import urllib.parse
import html
from datetime import datetime
from pprint import pprint
import textwrap


__version__ = "0.1.4"
# --- Configuration ---
FILE_TO_WATCH = "lcd.txt"  # The specific file to monitor
DIR_TO_WATCH = ".."             # Directory where the file exists

txt_color = (240, 240, 240)
shd_color = (20, 20, 20)
hl_type = 2

confile = 'config.yml'




script_path = os.path.dirname(os.path.abspath( __file__ ))
# set script path as current directory - 
os.chdir(script_path)

if os.path.exists('/dev/fb1'):
    fb = Framebuffer(1)
    #print("/dev/fb1 exists")
    # You can then proceed with code that uses the framebuffer
else:
    fb = Framebuffer(0)
    #print("/dev/fb1 does not exist")
    # Handle the case where the device is not available


def load_config(confile):
    '''
    {'back': {'blue': 0, 'green': 0, 'red': 0},
 'display': {'splash': 0},
 'text': {'blue': 55, 'green': 200, 'red': 255},
 'textbutton': {'gpio': 26},
 'texton': {'showtext': True}}

    '''
    x=1
    if path.exists(confile):
        #print('confile exists')
        global data
        with open(confile) as config_file:
            data = yaml.load(config_file, Loader=yaml.FullLoader)
            pprint(data)
            
            textz = data['text']
            txt_col = (textz['red'], textz['green'], textz['blue'])
            backz = data['back']
            bak_col = (backz['red'], backz['green'], backz['blue'])
            #bak_col = ImageColor.getrgb(colors['back'])
            
            display = data['display']
            splash = display['splash']
            return data

data = load_config(confile)

show_text = data['showtext']
but_num = data['textbutton']


def button_callback(channel):
    """Function to be called when the button is pressed."""
    # Change the boolean value when button presses
    global show_text
    show_text = not show_text
    #update display
    go_display()
    
    


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM)
# set gpio 26 (physical pin 37) as button pin
# this next to physical pin 39 - ground
BUTTON_PIN = but_num #
# Set the button pin as an input with an internal pull-up resistor
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Add event detection to the button pin. The function 'toggle_state' is called
# every time a falling edge is detected (button press when using PUD_UP).
# bouncetime prevents multiple rapid triggers from a single press.
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=500)

buffer = Image.new(mode="RGBA", size=fb.size)
start_img = Image.open(script_path + '/images/moode10-320x240.png')
im1 = Image.open(script_path + '/images/default-cover.png')
bar_img = Image.open(script_path + '/images/volbar.png').convert('RGBA')

buffer.paste(start_img)
fb.show(buffer)

font = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',28)
v_font = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',16)
i_font = ImageFont.truetype(script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf',16)
bi_font = ImageFont.truetype(script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf',128)

draw = ImageDraw.Draw(buffer,'RGBA')

color_but = (127,127,127)
volume = 47
volend = 280
volstart = 37

vollend = int((47/100) * (volend - volstart))

bluetooth = '\uf293'
airplay = '\uf01d'
spotify  = '\uf1bc'
sqp = '\uf01a'
mic  = '\uf130'
mic2  = '\uf3c9'
album  = '\uf00a'
next  = '\uf051'
prev  = '\uf048'
play  = '\uf04b'
pause  = '\uf04c'
stop  = '\uf04d'
cd  = '\uf51f'
bcasttower  = '\uf51f'
music  = '\uf001'
voldn  = '\uf027'
volup  = '\uf028'

source_char = {'bluetooth':'\uf293', 'airplay':'\uf01d', 'spotify' :'\uf1bc', 'lms':'\uf01a', 'library':'\uf00a', 'radio':'\uf3c9'}
fb.backlight(True)



def isServiceActive(service):

    waiting = True
    count = 0
    active = False

    while (waiting == True):

        process = subprocess.run(['systemctl','is-active',service], check=False, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        stat = output[:6]

        if stat == 'active':
            waiting = False
            active = True

        if count > 29:
            waiting = False

        count += 1
        time.sleep(1)

    return active

def change_display():
    print("Button Pressed")
    
def getMoodeMetadata(metafile):
    # Initalise dictionary
    metaDict = {}
    
    if path.exists(metafile):
        # add each line fo a list removing newline
        nowplayingmeta = [line.rstrip('\n') for line in open(metafile)]
        i = 0
        while i < len(nowplayingmeta):
            # traverse list converting to a dictionary
            (key, value) = nowplayingmeta[i].split('=',1)
            #value = html.unescape(value)
            metaDict[key] = value
            i += 1
        metaDict['artist'] = html.unescape(metaDict['artist'])
        metaDict['title'] = html.unescape(metaDict['title'])
        metaDict['coverurl'] = urllib.parse.unquote(metaDict['coverurl'])
        
        metaDict['source'] = 'library'
        if 'file' in metaDict:
            if (metaDict['file'].find('http://', 0) > -1) or (metaDict['file'].find('https://', 0) > -1):
                # set radio stream to true
                metaDict['source'] = 'radio'
                # if radio station has arist and title in one line separated by a hyphen, split into correct keys
                if metaDict['title'].find(' - ', 0) > -1:
                    (art,tit) = metaDict['title'].split(' - ', 1)
                    metaDict['artist'] = art
                    metaDict['title'] = tit
            elif metaDict['file'] == 'Squeezelite Active':
                metaDict['source'] = 'lms'
            elif metaDict['file'] == 'Spotify Active':
                metaDict['source'] = 'spotify'
            elif metaDict['file'] == 'Airplay Active':
                metaDict['source'] = 'airplay'
            elif metaDict['file'] == 'Bluetooth Active':
                metaDict['source'] = 'bluetooth'
                    
    # return metadata
    return metaDict



def get_cover(metaDict):
    
    cover = None
    cover = Image.open(script_path + '/images/default-cover.png')
    covers = ['Cover.jpg', 'cover.jpg', 'Cover.jpeg', 'cover.jpeg', 'Cover.png', 'cover.png', 'Cover.tif', 'cover.tif', 'Cover.tiff', 'cover.tiff',
		'Folder.jpg', 'folder.jpg', 'Folder.jpeg', 'folder.jpeg', 'Folder.png', 'folder.png', 'Folder.tif', 'folder.tif', 'Folder.tiff', 'folder.tiff']
    if metaDict['source'] == 'radio':
        if 'coverurl' in metaDict:
            if metaDict['coverurl'].startswith('http'):
                response = requests.get(metaDict['coverurl'])
                cover = Image.open(BytesIO(response.content)).resize((160,160), Image.LANCZOS)
                return cover
            else:
                rc = '/var/local/www/' + metaDict['coverurl']
                if path.exists(rc):
                    if rc != '/var/www/images/default-cover.png':
                        cover = Image.open(rc).convert("RGBA").resize((160,160), Image.LANCZOS)
                        return cover
    else:
        if 'file' in metaDict:
            if len(metaDict['file']) > 0:

                fp = '/var/lib/mpd/music/' + metaDict['file']
                
                if path.exists(fp):
                    mf = MediaFile(fp)   
                                     
                    if mf.art:
                        cover = Image.open(BytesIO(mf.art))
                        return cover
                    else:
                        for it in covers:
                            cp = os.path.dirname(fp) + '/' + it
                            
                            if path.exists(cp):
                                cover = Image.open(cp)
                                return cover
    return cover

def text_to_width (draw, text, font_path, font_size, location, fill_colour, outline_colour):
    if show_text is not True:
        return
    #font2 = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',28)
    #draw.text((160, 20), moode_meta['title'], fill=(255, 255, 255), font=font2, stroke_fill=(0,0,0), stroke_width=2, anchor="mm" )
    #font_size = 32
    target_width = 310
    #font_path = font
    font = ImageFont.truetype(font_path, font_size)
    # textbbox returns (x_min, y_min, x_max, y_max)
    text_width = draw.textbbox((0,0), text, font=font)[2]

    # Decrease font size until it fits
    while text_width > target_width and font_size > 12:
        font_size -= 1
        #print(font_size)
        font = ImageFont.truetype(font_path, font_size)
        text_width = draw.textbbox((0,0), text, font=font)[2]

    if font_size == 12:
        font = ImageFont.truetype(font_path, 16)
        wrapped_text = textwrap.wrap(text, width=40)
        #print(wrapped_text)
        
        y_text = location[1]
        for line in wrapped_text:
            #print (line)
            left, top, right, bottom = font.getbbox(line)
            height = bottom - top
            draw.text((160, y_text), line, font=font, fill=fill_colour,stroke_fill=outline_colour, stroke_width=1, anchor="mm" )
            y_text += height

        #draw.multiline_text(location, wrapped_text, fill=fill_colour, font=font,stroke_fill=outline_colour, stroke_width=1,  spacing=10, align='center')
    else:
        # Draw the text with the final font size
        draw.text(location, text, fill=fill_colour, stroke_fill=outline_colour, stroke_width=1, font=font, anchor="mm")




def go_display():
    global data
    '''if path.exists(confile):
        #print('confile exists')
        with open(confile) as config_file:
            data = yaml.load(config_file, Loader=yaml.FullLoader)
            pprint(data)'''
            
    textz = data['text']
    txt_col = (textz['red'], textz['green'], textz['blue'])
    backz = data['back']
    bak_col = (backz['red'], backz['green'], backz['blue'])
    #bak_col = ImageColor.getrgb(colors['back'])
            
    display = data['display']
    splash = display['splash']
         

    metafile = '../lcd.txt'
 
    c = 0
    title_top = 105
    

    client = musicpd.MPDClient()   # create client object
    try:     
        client.connect()           # use MPD_HOST/MPD_PORT
    except:
        pass
    else:                  
        moode_meta = getMoodeMetadata(metafile)
        
        mpd_current = client.currentsong()
                 
        mpd_status = client.status()

        #print(mpd_status)
               
        cover = get_cover(moode_meta)
        vol_w = 264
        c_vol = 0
        volstart = 47
            
               
        mn=0
        im_stat = ImageStat.Stat(cover) 
            
        im_mean = im_stat.mean
        r = im_mean[0]
        cb = 1
        mn = mean(im_mean)

                  
        enhancer = ImageEnhance.Brightness(cover)
            
        back = enhancer.enhance(0.5)
        buffer.paste(back.resize((360,360), Image.LANCZOS).filter(ImageFilter.GaussianBlur),(-20,-60))
            
        buffer.paste(cover.resize((220,220), Image.LANCZOS),(50,10))
        
        if moode_meta['source'] in ['radio', 'library', 'lms']:
            font2 = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',28)
            text_to_width (draw, moode_meta['title'], script_path + '/fonts/Roboto-Medium.ttf', 32, (160,20), txt_col, bak_col)
            text_to_width (draw, moode_meta['artist'], script_path + '/fonts/Roboto-Medium.ttf', 32, (160,70), txt_col, bak_col)
            text_to_width (draw, moode_meta['album'], script_path + '/fonts/Roboto-Medium.ttf', 32, (160,130), txt_col, bak_col)
               
        
        if 'source' in moode_meta:
            if moode_meta['source'] in ['bluetooth', 'airplay', 'spotify']:
                text_to_width (draw, source_char[moode_meta['source']], script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 128, (160,20), txt_col, bak_col)
            else:
                text_to_width (draw, source_char[moode_meta['source']], script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 16, (25,210), txt_col, bak_col)
                         
            if  moode_meta['source'] == 'library':
                text_to_width (draw, music, script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 16, (25,160), txt_col, bak_col)
                text_to_width (draw, moode_meta['track'], script_path + '/fonts/Roboto-Medium.ttf', 16, (25,185), txt_col, bak_col)
                text_to_width (draw, cd, script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 16, (300,160), txt_col, bak_col)
                text_to_width (draw, mpd_status['playlistlength'], script_path + '/fonts/Roboto-Medium.ttf', 16, (300,185), txt_col, bak_col)
                 
        if 'state' in moode_meta:
            if moode_meta['state'] == 'pause':
                text_to_width (draw, '\uf04c', script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 16, (300,210), txt_col, bak_col)
                
            elif moode_meta['state'] == 'play':
                text_to_width (draw, '\uf04b', script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 16, (300,210), txt_col, bak_col)
                
            elif moode_meta['state'] == 'stop':
                text_to_width (draw, '\uf04d', script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 16, (300,210), txt_col, bak_col)
                
        if 'volume' in moode_meta:
            c_vol = int(moode_meta['volume'])
            bar_w = int((c_vol/100) * vol_w)
            if bar_w < 1:
                bar_w = 1
                
            text_to_width (draw, 'VOL:', script_path + '/fonts/Font Awesome 5 Free-Solid-900.otf', 16, (25,230), txt_col, bak_col)
            if show_text is True:
                draw.rectangle((45,224,315,234  ), fill=None, outline=txt_col)
                draw.rectangle((46,225,bar_w+48,233), fill=txt_col)
            
        if splash == 1:
            if mpd_status['state'] == 'stop':
                buffer.paste(start_img)

            
        fb.show(buffer)
        
        #return moode_meta



class SpecificFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Check if the modified event is for our specific file
        if not event.is_directory and event.src_path.endswith(FILE_TO_WATCH):
            print(f"File Modified: {event.src_path}")
            # Add action here: e.g., read_file(event.src_path)
            #openLcdTxt()
            moode_meta = go_display()

async def main():
    
    #print("here")  
    moode_meta = go_display()
    #    moode_meta = go_display()
        
async def close():
    
    fb.clear()
    await asyncio.sleep(1)

if __name__ == '__main__':
    
    event_handler = SpecificFileHandler()
    observer = Observer()
    # Watch the directory for changes
    observer.schedule(event_handler, DIR_TO_WATCH, recursive=False)
    observer.start()
    
    #print(f"Watching for changes in: {FILE_TO_WATCH}...")
    moode_meta = go_display()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        #GPIO.cleanup()
        print()
    observer.join()

    

