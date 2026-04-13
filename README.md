

# update

The script will switch back to /dev/fb0 if /dev/fb1 is not created.

Thos may cuse issues if fb0 is too large, or if flashing cursors appear on your screen

The flashing curser can be stopped - google is your friend

The script will now auto adjust to match the display to framebuffer size

The script is designed for displays with a 4:3 aspect ratio with 320x240 as a starting point
Displays known to work are;
   2.8" ili9341
   2.0" ST7789x
   1.8" ST7735s - this is not exactly 4:3, but ts only a few pixels out

Framebuffers can be created by adding the coorresponding dtoverly line at the end of the /boot/firmware/config.txt file.
Ensure that spi is turned on by addeng or uncommenting the followung line in /boot/firmware/config.txt
```bash
   dtparam=spi=on
```

The overlays used for testing were:

Thear are built into Raspbian and don't need any extra installation

For 2.8" ili9341 (320x240)
```bash
dtoverlay=fbtft,spi0-0,ili9341,reset_pin=17,dc_pin=27,cs=0,led_pin=13,rotate=270,bgr=1
```

For 2.0" st7789v (320x240) also 1.9" (170x320)
```bash
dtoverlay=fbtft,spi0-0,st7789v,reset_pin=17,dc_pin=27,cs=0,led_pin=13,rotate=270
```

For 1.8" st7735s (160x128)
```bash
dtoverlay=fbtft,spi0-0,adafruit18,speed=32000000,reset_pin=17,dc_pin=27,led_pin=13,rotate=270
```

The pins used for reset, dc and backlight(led) were chosen to avoid pin conflicts with DAC hats.
If you use these overlays, connect the TFT as follows, otherwise edit the overlay line to suit your pin selection

| Display  |  RPi pin |  GPIO # |
|-|-|-|
| VCC | 1 | 3.3v |
| GND | 6 | gnd |
| CS | 24 | 8 |
| RESET | 11 | 17 |
| DC | 27 | 13 |
| SDI(MOSI) | 19 | 10 |
| SCK | 23 | 11 |
| LED | 33 | 13 |

The option to use up to 4 buttons for certain actions has been added

The config.yml file has been updated to allow which gpios are used

The 4 gpios were origanally chosen to prevent pin conflicts

They are

   GPIO 6 - Toggle text on / off
   GPIO 12 - toggle pause / play
   GPIO 4 - next track - library only
   GPIO 5 - previous track - library only



# prior update

The option to turn the text display on and off has been added.
i.e. When text display is off, only the cover art is shown

two nee options hav ebeen added to the config file to srt the startup option for this
and the GPIO number for adding a momentary pushbutton to toggle the text on/off
For ease of button connrctionI have made the config defaukt GOIO as 26 as the is physical pin 37 which is next 
to physical pin 39, which is ground. Of course you can change this to any free GPIO

make sure the correct python libray is installed by running the following
   ```bash
      sudo apt install python3-lgpio
   ```



# Note

The code for the framebuffer (framebuffer.py) is from http://github.com/robertmuth/Pytorinox

## Assumptions

1. You have Moode working on a Raspberry pi

2. You have an ILI9341 320*240 TFT display like this connected to the RPi:
   
    ![Image of Display](https://github.com/rusconi/Raspberry-Pi-TFT-FB1-HowTo/blob/master/images/screen.png)

3. The TFT displays /dev/fb1
   
    [Here is the HowTo on getting an ILI9341 TFT working as a framebuffer display](https://github.com/rusconi/Raspberry-Pi-TFT-FB1-HowTo)

## Preparation

In the MPD Options section of Moode's Audio Config;

* Ensure 'Metadata file' is on

In the Other peripherals section of Moode's PeripheralsConfig;

-  Ensure 'LCD updater' is on

## Installation

1. SSH into the RPi

2. Download the scripts
   
   ```bash
   git clone https://github.com/rusconi/moode_9341_fb.git
   ```

        cd into the moode_9341_fb directory



3. Install the required libraries     
   
   ```bash
   sudo apt install python3-watchdog python3-mediafile
   ```

4. Create the service file
   
   ```bash
   python create_service.py
   ```
   
   This will create the service file that will run the script on the RPi booting. The file
   
   is created to match the home directory
   
   the service file 'moode9341-fb.service' should look like;
   
   ```bash
   [Unit]
   Description=Moode 9341 Framebuffer Display
   After=mpd.socket mpd.service
   
   [Service]
   Type=idle
   User=root
   ExecStart=/usr/bin/python3 /home/pi/moode_9341_fb/moode_9341_fb.py
   ExecStop=/usr/bin/python3/home/pi/moode_9341_fb/clear_9641fb.py
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target
   
   ```
   
   with pi replaced by your chosen username

5. Install the service
   
   Run each of the following commands in this order:
   
   ```bash
       sudo cp moode9341-fb.service /lib/systemd/system/
       sudo chmod 644 /lib/systemd/system/moode9341-fb.service
       sudo systemctl enable moode9341-fb.service
       sudo systemctl daemon-reload
       sudo systemctl start moode9341-fb.service
       sudo systemctl status moode9341-fb.service
   ```
   
   the final output should look like this:
   
   ```bash
   moode9341-fb.service - Moode 9341 Framebuffer Display
        Loaded: loaded (/usr/lib/systemd/system/moode9341-fb.service; enabled; preset: enabled)
        Active: active (running) since Sun 2026-03-01 13:02:32 AEDT; 25s ago
    Invocation: a0a53c24f67042d1b1f8bb494f5d0c41
      Main PID: 17076 (python3)
         Tasks: 7 (limit: 1007)
           CPU: 2.247s
        CGroup: /system.slice/moode9341-fb.service
                └─17076 /usr/bin/python3 /home/pi/moode_9341_fb/moode_9341_fb.py
   
   ```

       The service should now be installed and will start on boot/reboot. 

        Be aware that the service should not start until mpd is running. this may take         some time.

### Configuration

The text display configuration is in the file config.yml

Use an online color picker to choose the color you want and the copy the RGB values to the 

corresponding places in config.yml

You can also change how to highlight text.

0. No highlight
1. outline
2. 
