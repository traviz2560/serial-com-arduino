# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 19:21:56 2020

"""

import serial,time
import serial.tools.list_ports
from tkinter import Frame,Label,Button,StringVar,ttk,Tk,NORMAL,DISABLED
from tkinter import messagebox
import datetime
import threading
import numpy as np
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Root(Tk):
    def __init__(self):
        super(Root,self).__init__()
        self.title('SENSOR DE TEMPERATURA')
        self.geometry('600x600')
        self.resizable(0,0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.connect_var = StringVar()
        self.text = StringVar()
        self.text.set('   C°')
        self.measure_state = False
        self.widgets()
        self.run = True
        self.protocol("WM_DELETE_WINDOW",self.salirfichero)
        self.minT = 10
        self.init = datetime.datetime.now()
        self.received = 0
        self.xs=[]
        self.ys=[]
        
    def salirfichero(self):
        valor=messagebox.askquestion('Salir','¿Desea cerrar la aplicacion?')
        if valor=='yes':
            self.run = False
            try:
                self.arduino.close()
                self.hilo.join(0.1)
            except:
                pass            
            self.destroy()
    
    def hidden(self):
        while self.run:
            if self.measure_state:
                try:
                    received = self.arduino.readline()
                    received = received.decode()
                    received = int(received)
                except ValueError:
                    received = 0
                self.received = received
                if received < self.minT:
                    self.text.set('No Data')
                else:
                    self.text.set(str(received)+' C°')

    def animate(self, i):
        if self.measure_state and self.text.get() != 'No Data':
            self.xs.append(datetime.datetime.now().strftime("%H:%M:%S"))
            self.ys.append(self.received)  
            self.xs = self.xs[-15:]
            self.ys = self.ys[-15:]
            self.ax.clear()
            self.ax.plot(self.xs,self.ys)
            self.ax.set_ylim(10,60)
            self.ax.set_yticks(np.arange(10, 60, 2), minor=True)
            self.ax.grid(True)
            self.fig.autofmt_xdate()
            self.canvas.draw()

    
    def start(self):
        port = self.port_list.get()
        baud = self.baud_list.get()
        if port != None and baud != '' :
            try:
              self.arduino = serial.Serial(port,baud,timeout=1)
            
            except serial.SerialException:
              serial.Serial(port, baud, timeout=1).close()
              self.arduino = serial.Serial(port,baud,timeout=3)
              pass
            
            time.sleep(1)
            self.connect_var.set('connected')
            self.hilo1 = threading.Thread(target=self.hidden)
            self.hilo1.setDaemon(True)
            self.hilo1.start()
            self.measure_button.config(state = NORMAL)
    
    def port_search(self):
        ports = list(serial.tools.list_ports.comports())
        arduino_ports=[]
        for port in ports:
            arduino_ports.append(port[0])
        self.port_list['values'] = arduino_ports
    
    def state(self):
        if (self.measure_button['text']=='MEDIR'):
            self.measure_button['text']='STOP'
            self.measure_state = True
        else:
            self.measure_button['text']='MEDIR'
            self.measure_state = False

        
    def widgets(self):
        frame = Frame(self)
        frame.grid(row=0, column=0, columnspan=3, sticky='ewns')
        frame.config(width=400,height=50)
        
        port_button = Button(frame, text='PUERTO',command = self.port_search)
        port_button.grid(row=0, column=0, padx=1, pady=1)
        
        self.port_list = ttk.Combobox(frame,state="readonly")
        self.port_list.grid(row=0, column=1, padx=2)
        self.port_list.config(width=10)
        
        self.baud_list = ttk.Combobox(frame,state="readonly")
        self.baud_list['values']=[9600,19200,38400,57600,115200,250000]
        self.baud_list.grid(row=0, column=2, padx=2)
        self.baud_list.config(width=10)
        
        connect_button = Button(frame, text='CONECTAR',command = self.start)
        connect_button.grid(row=0, column=3, padx=2)
        
        self.measure_button = Button(frame, text='MEDIR',state=DISABLED,command = self.state)
        self.measure_button.grid(row=0, column=4, padx=2)
        
        self.connect_var.set('disconnected')
        connect_message = Label(frame, textvariable=self.connect_var)
        connect_message.grid(row=0, column=5, padx=2)
        
        visual_frame = Frame(self)
        visual_frame.grid(row=1, column=0, columnspan=3, sticky='ewns')
        
        pantalla = Label(visual_frame,textvariable = self.text)
        pantalla.pack(padx=10,pady=10)
        pantalla.config(width=200,justify='center',font=("Courier", 60))
                        
        now = datetime.datetime.now()

        date = Label(self, text=now.strftime(" %A, %B %d, %Y"))
        date.grid(row=2,column=0,padx=10,pady=10,sticky='en')
        
        self.fig = Figure(figsize=(7, 4), dpi=100)
        self.fig.autofmt_xdate()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self) 
        self.canvas.get_tk_widget().grid(row=3,column=0,columnspan=3)
        self.ax = self.fig.add_subplot()
        self.ax.set_title('LM35 Temperature over Time')
        self.ax.set_ylabel('Temperature (C°)')
        self.ax.set_yticks(np.arange(10, 60, 2), minor=True)
        self.ax.grid(True)

        

root = Root()
ani = animation.FuncAnimation(root.fig, root.animate, interval=1000)
root.mainloop()