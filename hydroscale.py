import PySimpleGUI as sg  
import os.path
#import matplotlib
#import matplotlib.pyplot as pyplot
import numpy as np
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from DataRW import DataRW 
import re
from RxTx import RxTx
import schedule
# Layout
sg.theme('DarkTeal6')
layout = [[sg.Text("Welcome to the HydroScale GUI")],
[sg.Button('System Overview'), sg.Button('Past Logs')],
[sg.Button('Adjust Watering Times'),sg.Button('Add Module')],
[sg.Button('Turn Water On'), sg.Button('Turn Water Off')]]

# Create window
window = sg.Window('HydroScale', layout)
data = DataRW()
rxtx = RxTx()
schedules = []

def turn_on():
    titles = data.getTitles()
    titles.reverse()
    for title in titles:
        c1, c2, c3, c4, c5, c6 = data.getOnParameters(title)
        rxtx.txCode(c1, c2, c3, c4, c5, c6)
        time.sleep(8)
      
def turn_off():
    titles = data.getTitles()
    titles.reverse()
    for title in titles:
        c1, c2, c3, c4, c5, c6 = data.getOffParameters(title)
        rxtx.txCode(c1, c2, c3, c4, c5, c6)
        time.sleep(8)
# Display using an Event Loop
event, values = window.read()
while True:
    
    
    if event == 'System Overview':
        sg.Window('Overview', [[sg.Text("Current Water Content for sensor(i):"),sg.Text("0.34")],[sg.Input()],[sg.Button('Ok')]]).read(close=True)
    
    
    
    elif event == 'Past Logs':
        
       

        file_list_column = [
        [
        sg.Text("Logs Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
        ],
        [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
            )
         ],
        ]
        file_viewer_column = [
        [sg.Text("Choose an Log from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Canvas(key="-CANVAS-")],]
        layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(file_viewer_column,key=("-COL-"))
        ]
        ]
        window2 = sg.Window("Log Viewer", layout, finalize=True)
        
        matplotlib.use("TkAgg")
        def draw_figure(canvas, figure):
            figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
            figure_canvas_agg.draw()
            figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
            return figure_canvas_agg

        
        pyplot = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)

        pyplot.add_subplot(111).plot([10, 11, 12, 13, 14, 15],[0.98, 0.976, 0.973, 0.964, 0.960, 0.953])

        draw_figure(window2["-CANVAS-"].TKCanvas, pyplot)
        
        while True:
            event2, values2 = window2.read()
            if event2 == "Exit" or event2 == sg.WIN_CLOSED:
                break
        
        # Folder name was filled in, make a list of files in the folder
        if event2 == "-FOLDER-":
            folder = values2["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".png", ".gif"))
            ]
            window2["-FILE LIST-"].update(fnames)

        elif event2 == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                filename = os.path.join(
                    values2["-FOLDER-"], values2["-FILE LIST-"][0]
                )
                window2["-TOUT-"].update(filename)
                window2["-CANVAS-"].update(filename=filename)
            except:
                pass
        
    elif event == 'Adjust Watering Times':
        
        column_layout = [[sg.InputText(key="on"),sg.InputText(key="off")]]
        layout =[[sg.Text("Current Watering Schedules:")],
                 [sg.Text(schedule.get_jobs())],
                [sg.Column(column_layout, key='-Column-')],
                [sg.Button('Add Time')],[sg.Button('Clear All')]]



        window3 = sg.Window('Watering Times', layout)
        while True:
            event3, values = window3.read()
            if event3 == "Exit" or event3 == sg.WIN_CLOSED:
                    break
            
            if event3 == 'Add Time':
                event3_1, values = window3.read()
                schedule.every().day().at(values[0]).do(turn_on)
                schedule.every().day().at(values[1]).do(turn_off)
                
            if event3 == 'Clear All':
                schedule.clear()





    elif event == 'Turn Water On':
        titles = data.getTitles()
        titles.reverse()
        layoutOn = [[sg.Text("Select Module To Turn On")],
        *[[sg.Button(title),] for title in titles]]
        windowOn = sg.Window('Turn on', layoutOn)
        eventOn, valuesOn = windowOn.read()
        
        c1, c2, c3, c4, c5, c6 = data.getOnParameters(eventOn)
        rxtx.txCode(c1, c2, c3, c4, c5, c6)
        if eventOn == sg.WINDOW_CLOSED or eventOn == 'Quit':
            break

        

    elif event == 'Turn Water Off':
        titles = data.getTitles()
        titles.reverse()
        layoutOff = [[sg.Text("Select Module To Turn Off")],
        *[[sg.Button(title),] for title in titles]]
        windowOff = sg.Window('Turn on', layoutOff)
        eventOff, valuesOff = windowOff.read()
        
        c1, c2, c3, c4, c5, c6 = data.getOffParameters(eventOff)
        rxtx.txCode(c1, c2, c3, c4, c5, c6)
        if eventOff == sg.WINDOW_CLOSED or eventOff == 'Quit':
            break
        


    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    
    event, values = window.read()
# Never forget to clean up after yourself
rxtx.cleanup()
window.close()