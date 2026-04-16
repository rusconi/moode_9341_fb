# Other 320x240 pixel displays and overlays

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
| LED | 33 | 13 |xx


After connecting the display and editing config.txt reboot and ssh back into the pi

Test to see if framebuffer 1 (/dev/fbi) has been created

```bash
    ls /dev/fb1
```
if the respnse is
```bash
    /dev/fb1
```
then framebuffer 1 has been created.

get info about the framebuffer.

```bash
    fbset -fb /dev/fb1 --info
```
the result should be very close to this
```bash
    mode "320x240"
        geometry 320 240 320 240 16
        timings 0 0 0 0 0 0 0
        nonstd 1
        rgba 5/11,6/5,5/0,0/0
    endmode

    Frame buffer device information:
        Name        : fb_ili9340
        Address     : 0
        Size        : 153600
        Type        : PACKED PIXELS
        Visual      : TRUECOLOR
        XPanStep    : 0
        YPanStep    : 0
        YWrapStep   : 0
        LineLength  : 640
        Accelerator : 
```



