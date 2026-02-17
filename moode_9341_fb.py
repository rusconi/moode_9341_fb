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
from mediafile import MediaFile
from io import BytesIO
import math
from numpy import mean
import yaml
import urllib.parse
import html
from datetime import datetime


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


fb = Framebuffer(1)
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
#Font Awesome 5 Free-Solid-900.otf

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
            rc = '/var/local/www/' + metaDict['coverurl']
            if path.exists(rc):
                if rc != '/var/www/images/default-cover.png':
                    cover = Image.open(rc)
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

def text_in_rect(canvas, text, font, rect, line_spacing=1.1, align='center', color=(240,240,240), shd_color=(0,0,0), hlite=0):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
  
      
    # Given a rectangle, reflow and scale text to fit, centred
    while font.size > 0:
        space_width = font.getbbox(" ")[2]
        line_height = int(font.size * line_spacing)
        max_lines = math.floor(height / line_height)
        lines = []

        # Determine if text can fit at current scale.
        words = text.split(" ")

        while len(lines) < max_lines and len(words) > 0:
            line = []

            while len(words) > 0 and font.getbbox(" ".join(line + [words[0]]))[2] <= width:
                line.append(words.pop(0))

            lines.append(" ".join(line))

        if(len(lines)) <= max_lines and len(words) == 0:
            # Solution is found, render the text.
            y = int(rect[1] + (height / 2) - (len(lines) * line_height / 2) - (line_height - font.size) / 2)

            bounds = [rect[2], y, rect[0], y + len(lines) * line_height]

            for line in lines:
                line_width = font.getbbox(line)[2]
                if align == 'center':
                    x = int(rect[0] + (width / 2) - (line_width / 2))
                elif align == 'right':
                    x = int(rect[0] + width - line_width)
                elif align == 'left':
                    x = int(rect[0])
                            
                bounds[0] = min(bounds[0], x)
                bounds[2] = max(bounds[2], x + line_width)

                if hlite == 1:
                    # text outline
                    canvas.text((x-1, y), line, font=font, fill=shd_color, align=align)
                    canvas.text((x+1, y), line, font=font, fill=shd_color, align=align)
                    canvas.text((x, y-1), line, font=font, fill=shd_color, align=align)
                    canvas.text((x, y+1), line, font=font, fill=shd_color, align=align)
                elif hlite == 2:
                    canvas.text((x-2, y-2), line, font=font, fill=shd_color, align=align)
                    canvas.text((x-1, y-1), line, font=font, fill=shd_color, align=align)


                # light inner text
                canvas.text((x, y), line, font=font, fill=color, align=align)
                y += line_height

            return tuple(bounds)

        font = ImageFont.truetype(font.path, font.size - 1)


def go_display():

    #txt_col, bak_col, hl_type = loadConfig(confile)
    # Read config.yml for user config
    #txt_cl = (240,240,240)
    #shd_cl = (15,15,15)
    if path.exists(confile):
        #print('confile exists')
        with open(confile) as config_file:
            data = yaml.load(config_file, Loader=yaml.FullLoader)
            
            textz = data['text']
            txt_col = (textz['red'], textz['green'], textz['blue'])
            backz = data['back']
            bak_col = (backz['red'], backz['green'], backz['blue'])
            #bak_col = ImageColor.getrgb(colors['back'])
            highlight = data['highlight']
            hl_type = int(highlight['type'])
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

        '''if mn > 130:
            cb = 0.25
            if mn > 215:
                cb = 0.5
            txt_col = (55,55,55)
        else:
            txt_col = (200,200,200)'''
                
        enhancer = ImageEnhance.Brightness(cover)
            
        back = enhancer.enhance(0.5)
        buffer.paste(back.resize((360,360), Image.LANCZOS).filter(ImageFilter.GaussianBlur),(-20,-60))
            
        buffer.paste(cover.resize((220,220), Image.LANCZOS),(50,10))
        
        if moode_meta['source'] in ['radio', 'library', 'lms']:
            text_in_rect(draw, moode_meta['title'], font, (10,5,310,60), line_spacing=1.1, color=txt_col, shd_color=bak_col, hlite=hl_type)
            text_in_rect(draw, moode_meta['artist'], font, (10,70,310,125), line_spacing=1.1, color=txt_col, shd_color=bak_col, hlite=hl_type)
            text_in_rect(draw, moode_meta['album'], font, (25,130,295,215), line_spacing=1.1, color=txt_col, shd_color=bak_col, hlite=hl_type)
               
        
        if 'source' in moode_meta:
            if moode_meta['source'] in ['bluetooth', 'airplay', 'spotify']:
                text_in_rect(draw, source_char[moode_meta['source']], bi_font, (20,80,300,160), line_spacing=1.1, color=txt_col, shd_color=bak_col, hlite=hl_type)
            else:
                text_in_rect(draw, source_char[moode_meta['source']], i_font, (5,200,55,220), line_spacing=1.1, align='left', color=txt_col, shd_color=bak_col, hlite=hl_type)
                        
            if  moode_meta['source'] == 'library':
                text_in_rect(draw, music, i_font, (3,152,22,172), line_spacing=1.1, color=(txt_col), shd_color=(bak_col), hlite=hl_type)
                text_in_rect(draw, moode_meta['track'], v_font, (3,175,22,195), line_spacing=1.1, color=txt_col, shd_color=bak_col, hlite=hl_type)
                text_in_rect(draw, cd, i_font, (298,152,317,172), line_spacing=1.1, color=txt_col, shd_color=bak_col, hlite=hl_type)
                text_in_rect(draw, mpd_status['playlistlength'], v_font, (298,175,317,195), line_spacing=1.1, color=txt_col, shd_color=bak_col, hlite=hl_type)
                
        if 'state' in moode_meta:
            if moode_meta['state'] == 'pause':
                text_in_rect(draw, '\uf04c', i_font, (300,200,320,220), line_spacing=1.1, align='left', color=txt_col, shd_color=bak_col, hlite=hl_type)
                
            elif moode_meta['state'] == 'play':
                text_in_rect(draw, '\uf04b', i_font, (300,200,320,220), line_spacing=1.1, align='left', color=txt_col, shd_color=bak_col, hlite=hl_type)
                
            elif moode_meta['state'] == 'stop':
                text_in_rect(draw, '\uf04d', i_font, (300,200,320,220), line_spacing=1.1, align='left', color=txt_col, shd_color=bak_col, hlite=hl_type)
                
        if 'volume' in moode_meta:
            c_vol = int(moode_meta['volume'])
            bar_w = int((c_vol/100) * vol_w)
            if bar_w < 1:
                bar_w = 1
                
            text_in_rect(draw, 'VOL:', v_font, (5,220,65,240), line_spacing=1.1, align='left', color=txt_col, shd_color=bak_col, hlite=hl_type)
            
            draw.rectangle((45,224,315,234  ), fill=None, outline=txt_col)
            draw.rectangle((46,225,bar_w+48,233), fill=bak_col)
            #draw.rectangle((48,227,bar_w+46,231), fill=txt_col, outline=txt_col)

           
            #ibar = bar_img.resize((bar_w, 7), Image.LANCZOS)
            #buffer.paste(ibar, (volstart, 226), ibar)
        if splash == 1:
            if mpd_status['state'] == 'stop':
                buffer.paste(start_img)

            
        fb.show(buffer)

    
        '''
        # Each change creates a screen dump
        base_filename = "back"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        extension = ".png"
        new_filename = f"{base_filename}_{timestamp}{extension}"
        buffer.save(new_filename, format='png')
        '''
        
        return moode_meta
class SpecificFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Check if the modified event is for our specific file
        if not event.is_directory and event.src_path.endswith(FILE_TO_WATCH):
            print(f"File Modified: {event.src_path}")
            # Add action here: e.g., read_file(event.src_path)
            #openLcdTxt()
            moode_meta = go_display()

async def main():
    
    print()  
    #    moode_meta = go_display()
        
async def close():
    
    fb.clear()
    await asyncio.sleep(1)

if __name__ == '__main__':
    
    if not os.path.exists("../" + FILE_TO_WATCH):
        lcd_error_img = Image.open(script_path + '/images/lcd_file_error.png')
        buffer.paste(lcd_error_img)   
        fb.show(buffer)
        '''
            with open(FILE_TO_WATCH, "w") as f:
                f.write("Initial content\n")
            print(f"Created {FILE_TO_WATCH}")
        '''

    event_handler = SpecificFileHandler()
    observer = Observer()
    # Watch the directory for changes
    observer.schedule(event_handler, DIR_TO_WATCH, recursive=False)
    observer.start()
    
    print(f"Watching for changes in: {FILE_TO_WATCH}...")
    #moode_meta = go_display()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    

