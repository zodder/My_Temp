# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 11:37:16 2020

@author: zddan

@V1.00 
@V2.00  2020/10/09
@V2.10  2020/10/10
    1. fix the bug of exporting file name
    2. add the function to load raw data excel/csv file for id comparison
    3. add refresh button
    4. add the function to summarize how many files are imported correct or not, ensure the date load will not be terminated if the data is not correct
    5. fix other minor bugs
@V2.11 2020/10/16
    fix the bug of data exportation will remove the column of 'real_fixture_id'
@V2.20  2020/11/26
    Modify a lot of functions:
    1. fix several function bugs
    2. add retest calculation 
    3. add First yield calculation
@V2.21 2020/12/04
    1. modify some read data functions based on the data from other supplier
    2. Program is able to show the list of wrong data files and parts list which could not be searched
@V2.22 2020/12/11
    1. Create a new plugin called 'TestWindow' which contains sub-windows in usage
@V2.23 2020/12/23
    1. Finetune the function of data exportation - add the head in the csv file
    2. Fix the bug of data summary
@V0.2.24 2020/12/29
    1. Setup the main GUI for all the two functions
    2. Fix the issue when read some special csv file
    3. Add the function to read all csv, xlsx files in the defined folder
@V0.2.25 2021/01/16
    1. Fix one issue when facing the HEX data
    2. add the progressbar in the data analyst
@V0.2.26 2021/01/19
    1. Add the function to export the failed parts csv list in output folder
    2. fix one bug in folder description

"""

import sys
import tkinter as tk
from Data_combiner import dataCombiner
from OK2Ship_Reviewer import OK2D_Sorter


# from plugin.TestWindow import MainWindow

class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()

        self.missing_list = []
        self.title('Camera Test Data Assistant V0.2.25  --- by Amazon Camera SQM')
        self.geometry('640x480+300+200')

        self.logo = tk.Label(self, text='Camera Test Data Assistant', font=("微软雅黑", 24, "bold"))
        self.writer_name = tk.Label(self, text='By Amazon Camera SQM', font=('Arial', 12, 'bold', 'italic'))
        self.combiner_button = tk.Button(self, command=self.call_combiner,
                                         text="Data Analysis", font=('Arial', 11), width=40)
        self.sorter_button = tk.Button(self, command=self.call_sorter,
                                       text='OK2Delivery Reviewer', font=('Arial', 11), width=40)
        self.sfr_button = tk.Button(self, command=self.call_sfr_analyst,
                                    text='SFR Analyst', font=('Arial', 11), width=40, state='disabled')
        self.blemish_button = tk.Button(self, command=self.call_blemish_coor_analyst,
                                        text='Blemish Coordinate Analyst', font=('Arial', 11), width=40,
                                        state='disabled')
        self.quit_button = tk.Button(self, command=self.self_quit, text="Quit", font=('Arial', 10), width=20)

        self.ui_arrange()

    def ui_arrange(self):
        self.logo.place(x=100, y=40)
        self.writer_name.place(x=400, y=90)
        self.combiner_button.place(x=150, y=120)
        self.sorter_button.place(x=150, y=180)
        self.sfr_button.place(x=150, y=240)
        self.blemish_button.place(x=150, y=300)

        self.quit_button.place(x=240, y=400)

    def call_combiner(self):
        self.destroy()
        dC = dataCombiner()
        dC.wm_attributes('-topmost', 0)
        dC.mainloop()

        sys.exit(0)
        # self.deiconify()
        # self.wait_window(dC)

    def call_sorter(self):
        self.destroy()
        Sorter = OK2D_Sorter()
        Sorter.wm_attributes('-topmost', 0)
        Sorter.mainloop()
        # self.deiconify()
        sys.exit(0)

    def call_sfr_analyst(self):
        pass

    def call_blemish_coor_analyst(self):
        pass

    def self_quit(self):
        self.destroy()
        sys.exit(0)


if __name__ == '__main__':
    MW = MainWindow()
    MW.mainloop()
