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

"""

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as msgbox
import tkinter.scrolledtext as tkst
from tkinter import END
from tkinter import ttk
import sys
import os
import numpy as np
from plugin.TestData import TestData, DataFigure
from plugin.TestWindow import ErrorInfoList
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
# from matplotlib.figure import Figure

# af_folder = r'C:\MyWork\Work\Python\Camera_data_analysis\2306819'

class dataCombiner(tk.Tk):
    def __init__(self):

        super().__init__()

        self.missing_list = []
        self.title('Camera Test Data combiner V2.22  --- Authorwriter: Zhu Dan')
        self.geometry('820x640+100+80')

        self.test_data_path = tk.StringVar()
        self.test_data_file = tk.StringVar()
        self.label_test_data_path = tk.Label(self, text='Test Data path:')
        self.entry_test_data_path = tk.Entry(self, width=40, textvariable=self.test_data_path)
        self.label_test_data_file = tk.Label(self, text='Or Test Data File(csv or xlsx) path:')
        self.entry_test_data_file = tk.Entry(self, width=40, textvariable=self.test_data_file)
        self.config_path_button = tk.Button(self, command=self.load_data_path, text="Path", width=8)
        self.config_file_button = tk.Button(self, command=self.load_data_file, text="Load", width=8)
        self.yield_model = tk.IntVar()
        self.overall_yield_radio = tk.Radiobutton(self, text='Overall Yield', variable=self.yield_model,
                                                  command=self.refresh_data, value=1)
        self.final_yield_radio = tk.Radiobutton(self, text='Final Product Yield', variable=self.yield_model,
                                                command=self.refresh_data, value=2)
        self.first_yield_radio = tk.Radiobutton(self, text='First Pass Yield', variable=self.yield_model,
                                                command=self.refresh_data, value=3)
        self.yield_model.set(1)

        self.merge_data_button = tk.Button(self, command=self.merge_data, text="Import/Load", width=12)
        self.export_button = tk.Button(self, command=self.export_to_table, text="Export", width=12)
        self.split_station_fixture_button = tk.Button(self, command=self.split_fixture_data,
                                                      text="Station/Fixture Split", width=18)
        self.search_id_button = tk.Button(self, command=self.search_id, text="Search Parts", width=12)
        self.retest_data_button = tk.Button(self, command=self.calc_retest_data, text='Calc Retest', width=12)
        self.quit_button = tk.Button(self, command=self.self_quit, text="Quit", width=12)

        self.ui_arrange()

    def ui_arrange(self):
        self.label_test_data_path.place(x=40, y=40)
        self.label_test_data_file.place(x=40, y=80)
        self.entry_test_data_path.place(x=240, y=40)
        self.entry_test_data_file.place(x=240, y=80)
        self.config_path_button.place(x=500, y=35)
        self.config_file_button.place(x=500, y=75)
        # self.screen_retest_check.place(x=600, y=40)

        self.overall_yield_radio.place(x=600, y=35)
        self.final_yield_radio.place(x=600, y=55)
        self.first_yield_radio.place(x=600, y=75)

        self.merge_data_button.place(x=200, y=540)
        # self.refresh_data_button.place(x=280, y=540)
        self.export_button.place(x=360, y=540)
        self.search_id_button.place(x=520, y=540)
        self.split_station_fixture_button.place(x=160, y=580)
        self.retest_data_button.place(x=360, y=580)
        self.quit_button.place(x=520, y=580)

    def merge_data(self):
        '''
        Merge the data or directly load the data from the folder or file path input
        -------
        None.

        '''
        self.yield_df = pd.DataFrame()
        pathdir = self.test_data_path.get()
        filepath = self.test_data_file.get()
        if len(pathdir) == 0 and len(filepath) == 0:
            msgbox.showerror(title='Hi', message='No data resource is input')
        elif len(pathdir) > 0 and len(filepath) > 0:
            msgbox.showerror(title='Hi', message="Don't input folder or file information at the same time")
        else:
            if len(pathdir) > 0 and len(filepath) == 0:
                self.big_raw_data = TestData(pathdir=pathdir)
            elif len(pathdir) == 0 and len(filepath) > 0:
                self.big_raw_data = TestData(pathdir=filepath)
            self.refresh_data()

            msgbox.showinfo(title=None,
                            message="Total %d files are read and merged, \n %d files cannot be read correctly"
                                    % (len(self.big_raw_data.read_file_list), len(self.big_raw_data.wrong_file_list)))
            if len(self.big_raw_data.wrong_file_list) > 0:
                error_file_window = ErrorInfoList(desc_label='Error file names list:')
                
                error_file_window.title('Read Error Files')
                error_file_window.input_text(self.big_raw_data.wrong_file_list)
                self.wait_window(error_file_window)

        # print(self.big_raw_data.value.columns)

    def refresh_data(self):
        yield_model = self.yield_model.get()
        if yield_model == 2:
            self.raw_data = TestData(raw_data=self.big_raw_data.screen(inplace=False),
                                     spec=self.big_raw_data.spec, head_rows=self.big_raw_data.head_rows)
        elif yield_model == 1:
            self.raw_data = TestData(raw_data=self.big_raw_data.value,
                                     spec=self.big_raw_data.spec, head_rows=self.big_raw_data.head_rows)
            self.raw_data.calc_yield()
        elif yield_model == 3:
            self.raw_data = TestData(raw_data=self.big_raw_data.screen(inplace=False, how='first'),
                                     spec=self.big_raw_data.spec, head_rows=self.big_raw_data.head_rows)

        self.show_yield_pareto()

        # print(self.raw_data.stat_sum)

    def calc_retest_data(self):
        yield_model = self.yield_model.get()
        if yield_model == 2 or yield_model == 3:
            msgbox.showwarning(title=None,
                               message='Retest data are not included, please select "Overall yield model"')
        else:
            self.raw_data.calc_retest()
            retest_times = self.raw_data.retest_sum['Retest_times']
            retest_fig = DataFigure(axsize=[0.1, 0.1, 0.8, 0.8], figsize=(6, 5), dpi=60)
            retest_fig.hist_bar(input_data=retest_times, range=(3, retest_times.max()))
            retest_fig.ax.set_xlabel('Retest times', fontsize=12)
            retest_fig.ax.set_ylabel('Module count', fontsize=12)
            retest_fig.set_title('Retest Analysis')

            canvas_retest_times = FigureCanvasTkAgg(retest_fig.fig, master=self)
            canvas_retest_times.draw()
            canvas_retest_times.get_tk_widget().place(x=400, y=200)

    def split_fixture_data(self):
        print('Split the data according to the fixture')
        self.raw_data.calc_fixture()
        fixture_yield_fig = DataFigure(figsize=(6, 5), dpi=60, axsize=[0.18, 0.05, 0.75, 0.9])
        fixture_id = list(self.raw_data.multi_yield_df.index.tolist())
        yield_fixture_id = list(self.raw_data.multi_yield_df['PASS'])
        yield_fixture_dict = dict(zip(fixture_id, yield_fixture_id))
        fixture_yield_fig.yield_bar(input_data=yield_fixture_dict)

        canvas_fixture_yield = FigureCanvasTkAgg(fixture_yield_fig.fig, master=self)
        canvas_fixture_yield.draw()
        canvas_fixture_yield.get_tk_widget().place(x=400, y=200)

    def self_quit(self):
        self.destroy()
        sys.exit(0)

    def load_data_path(self):
        self.test_data_path.set(filedialog.askdirectory())

    def load_data_file(self):
        self.test_data_file.set(filedialog.askopenfilename())

    def split_station(self):
        self.raw_data.calc_fixture()

    def search_id(self):
        search_list_path = filedialog.askopenfilename()
        # print(search_list_path)
        if os.path.splitext(search_list_path)[1] in ['.txt', '.TXT']:
            with open(search_list_path) as search_list:
                s_id = search_list.read()
            s_id_list = s_id.split('\n')
            if s_id_list[-1] == '':
                s_id_list.remove('')
            s_id_list = [single_id.replace("'","") for single_id in s_id_list]
        elif os.path.splitext(search_list_path)[1] in ['.csv', '.CSV', '.XLS', '.xls', '.xlsx', 'XLSX']:
            new_device_list = TestData(pathdir=search_list_path)
            s_id_list = list(new_device_list.uni_serial)
        # print(s_id_list)
        msgbox.showinfo(title=None, message='Total %d seiral IDs are loaded' % len(s_id_list))
        # self.raw_data.missing_list = self.raw_data.search_id(s_id_list, inplace=True)
        self.raw_data.search_id(s_id_list)
        self.raw_data.calc_yield()
        self.show_yield_pareto()
        # print(self.missing_list)
        if len(self.raw_data.missing_list) > 0:
            msgbox.showwarning(title=None, message='%d parts cannot be found' % len(self.raw_data.missing_list))
            missing_window = ErrorInfoList(desc_label='Missing Parts list:')
            missing_window.title('Missing Parts List')
            missing_window.input_text(self.raw_data.missing_list)
            self.wait_window(missing_window)

    def export_to_table(self):
        target_name = filedialog.asksaveasfilename(title='Save to excel file')
        if target_name == '':
            msgbox.showerror(title=None, message='No export table name defined!')
        else:
            if not (os.path.splitext(target_name)[1] in ['.csv', '.CSV']):
                csv_target_name = target_name + '.csv'

            else:
                csv_target_name = target_name
            excel_target_name = os.path.splitext(target_name)[0] + '_yield_summary.xlsx'

        # print(self.raw_data.stat_sum)
        self.raw_data.export_to_excel(csv_target_name, excel_target_name)
        msgbox.showinfo(title=None, message='Finish the data exportation!')

    def show_yield_pareto(self):
        self.yield_df = pd.DataFrame()
        self.raw_data.calc_yield()
        self.yield_df = pd.concat([self.yield_df, self.raw_data.yield_df])

        # pie_fig = DataFigure()
        # pie_fig.ring(input_data=self.raw_data.fail_yield_dict, autopct='%1.2f%%')
        # pie_fig.set_title('Fail Bin pareto(Total Count: ' + str(self.raw_data.fail_count) + ')',
        #                  fontsize=20, fontweight='bold')

        bar_fig = DataFigure(axsize=[0.1, 0.3, 0.8, 0.6])
        if len(self.raw_data.fail_yield_dict) == 0:
            bar_fig.pareto_bar(input_data={'PASS': 1})
            bar_fig.set_title('All Pass(Total count:' + str(self.raw_data.module_count) + ')')
        else:
            bar_fig.pareto_bar(input_data=self.raw_data.fail_yield_dict)
            bar_fig.set_title('Fail Bin pareto(Total Count: ' + str(self.raw_data.fail_count) + '/' + str(
                self.raw_data.module_count) + ')')

        canvas_pareto = FigureCanvasTkAgg(bar_fig.fig, master=self)  # A tk.DrawingArea.
        canvas_pareto.draw()
        canvas_pareto.get_tk_widget().place(x=20, y=120)

        main_yield_fig = DataFigure(figsize=(6, 1), dpi=60, axsize=[0.18, 0.05, 0.75, 0.9])
        main_yield_fig.yield_bar(input_data={'Whole Yield': self.raw_data.yield_value})

        canvas_main_yield = FigureCanvasTkAgg(main_yield_fig.fig, master=self)
        canvas_main_yield.draw()
        canvas_main_yield.get_tk_widget().place(x=400, y=120)


    def hide_yield_bar(self):
        pass


if __name__ == '__main__':
    combiner = dataCombiner()
    combiner.mainloop()
