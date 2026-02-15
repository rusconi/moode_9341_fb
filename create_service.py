import os

current_directory = os.getcwd()

first_lines = ["[Unit]\n","Description=Moode tft Framebuffer Display\n","Requires=mpd.socket mpd.service\n","After=mpd.socket mpd.service\n","\n","[Service]\n","Type=simple\n"]
exec_one = "ExecStart=/usr/bin/python3 " + current_directory + "/moode_9341_fb.py\n"
exec_two = "ExecStop=" + current_directory + "/moode9341-fb.sh -q\n"
last_lines = ["Restart=on-abort\n","\n","[Install]\n","WantedBy=multi-user.target"]

with open('moode9341-fb.service', 'w') as f:
    f.writelines(first_lines)
    f.writelines(exec_one)
    f.writelines(exec_two)
    f.writelines(last_lines)
    