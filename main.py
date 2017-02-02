#Creating a kivy application is as simple as:
#sub-classing the App class
#implementing its build() method so it returns a Widget instance (the root of your widget tree)
#instantiating this class, and calling its run() method.
#Here is an example of a minimal application://

from kivy.config import Config
Config.set('graphics','fullscreen','auto')
Config.write()
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, BorderImage
import kivy.core
import json
import serial
import time
from datetime import datetime
import pymysql.cursors


#Class representing each batchmaker. update_colors() is called for each batchmaker during BatchmakerDisplay().update()
class Batchmaker(BoxLayout,Widget):
    probe = NumericProperty(0)
    temp = NumericProperty(0)
    name = StringProperty('')
    colour = ListProperty([3])
            
    def update_colors(self):
        self.colour=[0.161,1,1,1]
        if self.temp  <= 40:
            self.colour=[0,1,0,1]
        elif self.temp  <= 48:
            self.colour=[0.823,1,0.302,1]   
        elif self.temp  <= 55:
            self.colour=[1,1,0,1]
        elif self.temp  <= 70:
            self.colour=[1,0.839,0.2,1]
        elif self.temp  <= 90:
            self.colour=[1,0.38,0,1]
        elif self.temp  <= 105:
            self.colour=[1,0.28,0,1]
        else: 
            self.colour=[1,0,0,1]
            
    def __init__(self, *args, **kwargs):
        super(Batchmaker, self).__init__(*args, **kwargs)    
        

#primary class of the app. initializes the Batchmaker() objects and updates their temperatures.
class BatchmakerDisplay(GridLayout,Widget):
    m601 = ObjectProperty(None)
    m602 = ObjectProperty(None)
    m603 = ObjectProperty(None)
    m604 = ObjectProperty(None)
    m281 = ObjectProperty(None)
    m282 = ObjectProperty(None)
    m283 = ObjectProperty(None)
    m91 = ObjectProperty(None)
    m92 = ObjectProperty(None)
    batchmakerids = ['m601','m602','m603','m604','m281','m282','m283','m91','m92']
    batchtemps = [0.0] * 9
    probenum = 0
    temperature = 0.0
    datetimes = [datetime.now()] * 9

    def update(self,dt):
        self.iteration = 0
        self.msg = ""
        self.msg=self.ser.read(1000)
        try:
            i=0
            while i <= (len(self.msg) - 10):
                if self.msg[i] == 'e':
                    self.probenum=int(self.msg[i+2])
                    self.temperature=float(self.msg[(i+5):(i+10)])
                    self.batchtemps[self.probenum-1]=self.temperature
                    self.datetimes[self.probenum-1]=datetime.now()
                i=i+1
        except:
            pass
        for child in self.children: 
            child.temp = self.batchtemps[int(child.probe)-1]
            child.update_colors()

    def upload_data(self,dt):
        connection = pymysql.connect(host='localhost', user='tim', password='Skipper254?', database='batchtemps', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                i=0
                # Create a new record
                while i<9:
                    cursor.execute("INSERT INTO data (batchmaker,temp,date_time) VALUES (%s, %s, %s)",(self.batchmakerids[i], self.batchtemps[i],self.datetimes[i]))
                    connection.commit()
                    i=i+1
        finally:
            connection.close()

    def __init__(self, *args, **kwargs):
        super(BatchmakerDisplay, self).__init__(*args, **kwargs)
        self.ser = serial.Serial('COM9', baudrate=230400, timeout=0)
        time.sleep(3)
        Clock.schedule_interval(self.update, 1)
        Clock.schedule_interval(self.upload_data,10)

class BatchmakerApp(App):
    def build(self):
        return BatchmakerDisplay()

if __name__ == '__main__':
    BatchmakerApp().run()