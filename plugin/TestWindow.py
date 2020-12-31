# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 06:58:54 2020

@author: zddan
"""

import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import END

import sys

class ErrorInfoList(tk.Toplevel):
    def __init__(self, desc_label='Error list', geo='500x200+300+200'):
        super().__init__()

        self.geometry(geo)
        self.text_content = tkst.ScrolledText(self, width=60, height=6, font=("Arial", 9))
        self.OK_button = tk.Button(self, command=self.quit_prog, text='OK', width=10)
        
        self.desc_label = tk.Label(self, text=desc_label)
        self.ui_arrange()
    
    def ui_arrange(self):
        self.desc_label.place(x=20, y=20)
        self.text_content.place(x=20, y=45)
        self.OK_button.place(x=220, y=160)

    def input_text(self, input_text):
        for single_text in input_text:
            self.text_content.insert(END, single_text + '\n')

    def quit_prog(self):
        self.destroy()
        

