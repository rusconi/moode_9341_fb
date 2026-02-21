import os

current_directory = os.getcwd()

first_lines = ["[Unit]\n","Description=Moode 9341 Framebuffer Display\n","After=mpd.socket mpd.service\n","\n","[Service]\n","Type=idle\n","User=root\n"]
exec_one = "ExecStart=/usr/bin/python3 " + current_directory + "/moode_9341_fb.py\n"
last_lines = ["Restart=on-failure\n","\n","[Install]\n","WantedBy=multi-user.target"]

with open('moode9341-fb.service', 'w') as f:
    f.writelines(first_lines)
    f.writelines(exec_one)
    f.writelines(last_lines)
    