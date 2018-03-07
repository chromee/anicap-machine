import os
from rails_connector import RailsConnector


dir=r"D:/downloads/tmp/"
files = os.listdir(dir)
rc = RailsConnector("http://192.168.99.100:3000/captures/")
for file in files:
    print(dir+file)
    rc.send_picture(dir+file)
