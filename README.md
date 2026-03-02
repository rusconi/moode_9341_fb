

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
