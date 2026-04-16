
# Note

The code for the framebuffer (framebuffer.py) is from http://github.com/robertmuth/Pytorinox

The script will switch back to /dev/fb0 if /dev/fb1 is not created.
This may cause issues if fb0 is too large, or if flashing cursors appear on your screen

The script can auto adjust to framebuffers of different sizes.
This may not look good on displays karger than 320x340 pixels


## Assumptions

1. You have Moode working on a Raspberry pi

2. You have an ILI9341 320*240 TFT display like this connected to the RPi:
   
    ![Image of Display](https://github.com/rusconi/Raspberry-Pi-TFT-FB1-HowTo/blob/master/images/screen.png)

3. The TFT displays /dev/fb1 (or fb0 if fb1 is not available)
   
    [Here is the HowTo on getting an ILI9341 TFT working as a framebuffer display](https://github.com/rusconi/Raspberry-Pi-TFT-FB1-HowTo)

    [Other options for framebuffers are also available.](Other_displays.md)

    Iy doesn't matter which framebuffer method is used as long as you connect the display to the RPI GPOs that maych the overlay file you use.

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

## Other Functions and config file

The option to turn use some pushbuttons been added.

Up to 4 pushbuttons can be added.

Use momentary action switches

The functions these buttons control are:

- Toggle the text display on/off. The coverart is always displayed.
- Toggle pause/play.
- Next track
- Previous track,

The GPIO pins used to connect the buttons to can be edited in the config file (config.yml)

The 4 gpios were origanally chosen to prevent pin conflicts

They are

   GPIO 6 - Toggle text on / off
   GPIO 12 - toggle pause / play
   GPIO 4 - next track - library only
   GPIO 5 - previous track - library only

Text display colors can be changed in the config file as well

Use an online color picker to choose the color you want and the copy the RGB values to the 

corresponding places in config.yml

You can also change how to highlight text.

0. No highlight
1. outline
