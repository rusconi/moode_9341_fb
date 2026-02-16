# versions
0.0.1 - initial version for moode 6.5.2

0.0.2 - update for changed location of radio icons
# moode_9341_fb
Moode now playing on TFT framebuffer (/dev/fb1)

0.1.4 - update for change on moode coverurl

0.2.0 - change of name to moode_9341_fb
      - updated to run on moode 10.1.0

# Note

The code for the framebuffer (framebuffer.py) is from http://github.com/robertmuth/Pytorinox

## Assumptions ##

1. You have Moode working on a Raspberry pi

2. You have an ILI9341 320*240 TFT display like this connected to the RPi:

    ![Image of Display](https://github.com/rusconi/Raspberry-Pi-TFT-FB1-HowTo/blob/master/images/screen.png)

3. The TFT displays /dev/fb1

    [Here is the HowTo on getting an ILI9341 TFT working as a framebuffer display](https://github.com/rusconi/Raspberry-Pi-TFT-FB1-HowTo)

4. You have git installed on your pi

## Preparation ##

In the Local Services section of Moode's System Config;

* Ensure 'Metadata file' is on : Configure -> Audio -> MPD Options -> Metadata file
* Ensure 'LCD Updater' is on : Configure -> Peripherals -> MPD Other peripherals -> LCD updater


## Installation ##

1. SSH into the RPi

2. Download the scripts

    ```bash
    git clone https://github.com/rusconi/moode_9341_fb.git
    cd /home/pi/moode_9341_fb
    ```

3. Install the required python libraries

    ```bash
    sudo apt install python3-watchdog python3-mediafile
    ```

4. Install python scripts

    Before running the install script, you need to create a moode9341-fb.service file to suit your username.

    ```bash
    python create_service.py
    ```
    This will create the file moode9341-fb.service to match your username setup.
    It will look something like this

      [Unit]
      Description=Moode 9341 Framebuffer Display
      After=mpd.socket mpd.service
      
      [Service]
      Type=idle
      User=root
      ExecStart=/usr/bin/python3 /home/[your username]/moode_9341_fb/moode_9341_fb.py
      Restart=always # Restart if it fails
      
      [Install]
      WantedBy=multi-user.target # Standard target for normal boot

   Set the shell scripts t executable:

   ```bash
    chmod +x moode_9341_fb.py framebuffer.py install-moode-9341-fb.sh moode9341-fb.sh clear_9341fb.py
   ```


    run the servce install script. This will install, prepare, and start the service

    ```bash
    ./install-moode-9341-fb.sh
    ```


    
 ### Configuration ###

 The text display configuration is in the file config.yml

 Use an online color picker to choose the color you want and the copy the RGB values to the 

 corresponding places in config.yml

 You can also change how to highlight text.
 
 0. No highlight
 1. outline
 2. shadow

 
