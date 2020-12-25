# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 16:50:39 2020

@author: zddan
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as msgbox
from plugin.TestData import TestData
from plugin.TestWindow import ErrorInfoList
from datetime import datetime


def return_time_str():
    nowtime = datetime.now()
    return nowtime.strftime("%Y%m%d%H%M%S")

def log_print(log, txt):
    print(txt)
    log.write(txt)


class shipScreener(tk.Tk):
    def __init__(self):

        super().__init__()
        
        self.compare_data_dict = []
        self.settings = {}


        self.title('Camera Test OK2ship Screener V0.01  --- Authorwriter: Zhu Dan')
        self.geometry('820x640+100+80')
        
        self.ok2ship_data_path = tk.StringVar()
        self.label_ok2ship_path = tk.Label(self, text='Pending for OK2Delivery parts list folder:')
        self.entry_ok2ship_path = tk.Entry(self, width=40, textvariable=self.ok2ship_data_path)
        
        self.output_data_path = tk.StringVar()
        self.label_output_path = tk.Label(self, text='Output Data Path:')
        self.entry_output_path = tk.Entry(self, width=40, textvariable=self.output_data_path)
        
        self.label_data_type = tk.Label(self, text='Data Stage')
        self.label_data_link = tk.Label(self, text='Data Folder')
        self.label_allowed_retest = tk.Label(self, text='Maximum Allowed Times\n(0 means no limit)')
        
        #self.data_type1 = tk.StringVar()
        self.data_link1 = tk.StringVar()
        self.retest_allowed1 = tk.IntVar()
        #self.entry_data_type1 = tk.Entry(self, width=12, textvariable=self.data_type1)
        self.combo_data_type1 = ttk.Combobox(width=12)
        self.combo_data_type1['value'] = ['AF_UP', 'AF_DOWN', 'CCL', 'FQC', 'OBA']
        self.entry_data_link1 = tk.Entry(self, width=40, textvariable=self.data_link1)
        self.entry_retest_allowed1 = tk.Entry(self, width=12, textvariable=self.retest_allowed1)
        
        # self.data_type2 = tk.StringVar()
        self.data_link2 = tk.StringVar()
        self.retest_allowed2 = tk.IntVar()
        self.combo_data_type2 = ttk.Combobox(width=12)
        self.combo_data_type2['value'] = ['AF_UP', 'AF_DOWN', 'CCL', 'FQC', 'OBA']
        self.entry_data_link2 = tk.Entry(self, width=40, textvariable=self.data_link2)
        self.entry_retest_allowed2 = tk.Entry(self, width=12, textvariable=self.retest_allowed2)
        
        # self.data_type3 = tk.StringVar()
        self.data_link3 = tk.StringVar()
        self.retest_allowed3 = tk.IntVar()
        self.combo_data_type3 = ttk.Combobox(width=12)
        self.combo_data_type3['value'] = ['AF_UP', 'AF_DOWN', 'CCL', 'FQC', 'OBA']
        self.entry_data_link3 = tk.Entry(self, width=40, textvariable=self.data_link3)
        self.entry_retest_allowed3 = tk.Entry(self, width=12, textvariable=self.retest_allowed3)
        
        # self.data_type4 = tk.StringVar()
        self.data_link4 = tk.StringVar()
        self.retest_allowed4 = tk.IntVar()
        self.combo_data_type4 = ttk.Combobox(width=12)
        self.combo_data_type4['value'] = ['AF_UP', 'AF_DOWN', 'CCL', 'FQC', 'OBA']
        self.entry_data_link4 = tk.Entry(self, width=40, textvariable=self.data_link4)
        self.entry_retest_allowed4 = tk.Entry(self, width=12, textvariable=self.retest_allowed4)
        
        # self.data_type5 = tk.StringVar()
        self.data_link5 = tk.StringVar()
        self.retest_allowed5 = tk.IntVar()
        self.combo_data_type5 = ttk.Combobox(width=12)
        self.combo_data_type5['value'] = ['AF_UP', 'AF_DOWN', 'CCL', 'FQC', 'OBA']
        self.entry_data_link5 = tk.Entry(self, width=40, textvariable=self.data_link5)
        self.entry_retest_allowed5 = tk.Entry(self, width=12, textvariable=self.retest_allowed5)
        
        # self.data_type6 = tk.StringVar()
        self.data_link6 = tk.StringVar()
        self.retest_allowed6 = tk.IntVar()
        self.combo_data_type6 = ttk.Combobox(width=12)
        self.combo_data_type6['value'] = ['AF_UP', 'AF_DOWN', 'CCL', 'FQC', 'OBA']
        self.entry_data_link6 = tk.Entry(self, width=40, textvariable=self.data_link6)
        self.entry_retest_allowed6 = tk.Entry(self, width=12, textvariable=self.retest_allowed6)
        
        self.start_button = tk.Button(self, command=self.screen, text="Start", width=12)
        self.quit_button = tk.Button(self, command=self.self_quit, text="Quit", width=12)
        self.load_settings_button = tk.Button(self, command=self.load_settings, text='Load settings', width=15)
        self.save_settings_button = tk.Button(self, command=self.save_settings, text='Save settings', width=15)
                
        self.ui_arrange()
        
    def ui_arrange(self):
        self.label_ok2ship_path.place(x=40, y=100)
        self.entry_ok2ship_path.place(x=300, y=100)
        
        self.label_output_path.place(x=40, y=540)
        self.entry_output_path.place(x=300, y=540)
        
        self.start_button.place(x=80, y=600)
        self.quit_button.place(x=560, y=600)
        self.save_settings_button.place(x=240, y=600)
        self.load_settings_button.place(x=400, y=600)
        
        self.label_data_type.place(x=40, y=150)
        self.label_data_link.place(x=160, y=150)
        self.label_allowed_retest.place(x=400, y=150)
        
        #self.entry_data_type1.place(x=30, y=200)
        self.combo_data_type1.place(x=30,y=200)
        self.entry_data_link1.place(x=150,y=200)
        self.entry_retest_allowed1.place(x=430, y=200)
        
        self.combo_data_type2.place(x=30,y=250)
        self.entry_data_link2.place(x=150,y=250)
        self.entry_retest_allowed2.place(x=430, y=250)
               
        self.combo_data_type3.place(x=30,y=300)
        self.entry_data_link3.place(x=150,y=300)
        self.entry_retest_allowed3.place(x=430, y=300)

        self.combo_data_type4.place(x=30, y=350)
        self.entry_data_link4.place(x=150,y=350)
        self.entry_retest_allowed4.place(x=430, y=350)
        
        self.combo_data_type5.place(x=30, y=400)
        self.entry_data_link5.place(x=150,y=400)
        self.entry_retest_allowed5.place(x=430, y=400)

        self.combo_data_type6.place(x=30, y=450)
        self.entry_data_link6.place(x=150,y=450)
        self.entry_retest_allowed6.place(x=430, y=450)
        
        self.ok2ship_data_path.set('.\OK2D_Data\OK2Delivery')
        self.output_data_path.set('.\OK2D_Data\Output')
        
        self.data_link1.set('.\OK2D_Data\AF_UP')
        self.data_link2.set('.\OK2D_Data\AF_DOWN')
        self.data_link3.set('.\OK2D_Data\CCL')
        self.data_link4.set('.\OK2D_Data\FQC')
        self.data_link5.set('.\OK2D_Data\OBA')
        
        self.combo_data_type1.current(0)
        self.combo_data_type2.current(1)
        self.combo_data_type3.current(2)
        self.combo_data_type4.current(3)
        self.combo_data_type5.current(4)

        
    def self_quit(self):
        self.destroy()
        sys.exit(0)

    
    def save_settings(self):
        self.collect_comp_data()
        self.settings = {'ok2ship_path': self.ok2ship_data_path.get(),
                         'output_path': self.output_data_path.get(),
                         'compare_data_dict': self.compare_data_dict}
        settings_json = json.dumps(self.settings)
        json_path = filedialog.asksaveasfilename(title='Save Setting Files', filetypes=[("JSON", ".json")])
        if json_path == '':
            msgbox.showerror(title=None, message='No export table name defined!')
        else:
            if not (os.path.splitext(json_path)[1] in ['json', '.JSON']):
                json_path = json_path + '.json'
            with open(json_path, 'w') as json_f:
                json.dump(settings_json, json_f)
            msgbox.showinfo(title=None, message='Already save the settings')

    
    def load_settings(self):
        target_json = filedialog.askopenfilename(title='Load Json Setting Files',  filetypes=[("JSON", ".json")])
        with open(target_json, 'r') as jason_f:
            loaded_settings = json.load(jason_f)
        json_loaded = json.loads(loaded_settings)
        self.ok2ship_data_path.set(str(json_loaded['ok2ship_path']))
        self.output_data_path.set(str(json_loaded['output_path']))
        data_info_dict = json_loaded['compare_data_dict']
        
        len_data = len(data_info_dict)
        if len_data > 0:
            data1_dict = data_info_dict[0]
            self.combo_data_type1.set(data1_dict['type'])
            self.data_link1.set(data1_dict['link'])
            self.retest_allowed1.set(int(data1_dict['retest']))
        if len_data > 1:
            data2_dict = data_info_dict[1]
            self.combo_data_type2.set(data2_dict['type'])
            self.data_link2.set(data2_dict['link'])
            self.retest_allowed2.set(int(data2_dict['retest']))
        if len_data > 2:
            data3_dict = data_info_dict[2]
            self.combo_data_type3.set(data3_dict['type'])
            self.data_link3.set(data3_dict['link'])
            self.retest_allowed3.set(int(data3_dict['retest']))
        if len_data > 3:
            data4_dict = data_info_dict[3]
            self.combo_data_type4.set(data4_dict['type'])
            self.data_link4.set(data4_dict['link'])
            self.retest_allowed4.set(int(data4_dict['retest']))
        if len_data > 4:
            data5_dict = data_info_dict[4]
            self.combo_data_type5.set(data5_dict['type'])
            self.data_link5.set(data5_dict['link'])
            self.retest_allowed5.set(int(data5_dict['retest']))            
        if len_data > 5:
            data6_dict = data_info_dict[5]
            self.combo_data_type6.set(data6_dict['type'])
            self.data_link6.set(data6_dict['link'])
            self.retest_allowed6.set(int(data6_dict['retest'])) 
        
        msgbox.showinfo(title=None, message='Already load the settings')
    
    def collect_comp_data(self):
        self.compare_data_dict = []
        if len(self.combo_data_type1.get())>0:
            data1_dict = {'type': self.combo_data_type1.get(),
                          'link': self.data_link1.get(),
                          'retest': self.retest_allowed1.get()
                }
            self.compare_data_dict.append(data1_dict)
            
        if len(self.combo_data_type2.get())>0:
            data2_dict = {'type': self.combo_data_type2.get(),
                          'link': self.data_link2.get(),
                          'retest': self.retest_allowed2.get()
                }
            self.compare_data_dict.append(data2_dict)
            
        if len(self.combo_data_type3.get())>0:
            data3_dict = {'type': self.combo_data_type3.get(),
                          'link': self.data_link3.get(),
                          'retest': self.retest_allowed3.get()
                }
            self.compare_data_dict.append(data3_dict)

        if len(self.combo_data_type4.get())>0:
            data4_dict = {'type': self.combo_data_type4.get(),
                          'link': self.data_link4.get(),
                          'retest': self.retest_allowed4.get()
                }
            self.compare_data_dict.append(data4_dict)
            
        if len(self.combo_data_type5.get())>0:
            data5_dict = {'type': self.combo_data_type5.get(),
                          'link': self.data_link5.get(),
                          'retest': self.retest_allowed5.get()
                }
            self.compare_data_dict.append(data5_dict)
            
        if len(self.combo_data_type6.get())>0:
            data5_dict = {'type': self.combo_data_type6.get(),
                          'link': self.data_link6.get(),
                          'retest': self.retest_allowed6.get()
                }
            self.compare_data_dict.append(data5_dict)
    
    def screen(self):
        
        if len(self.ok2ship_data_path.get()) == 0:
            msgbox.showerror('None', 'No ok2ship folder is defined!')
        elif len(self.output_data_path.get()) == 0:
            msgbox.showerror('None', 'No oupput folder is defined!')
        else:
            start_time_str = str(return_time_str())
            self.target_datalog = os.path.join(self.output_data_path.get(), 'Output_datalog_' + start_time_str + '.txt')
            
            with open(self.target_datalog, 'w') as datalog:
                print('\n\n\n')

                log_print(datalog, 'Start to check the OK2Delivery parts in the folder of %s at the time of %s ... \n\n' % (self.output_data_path.get(), start_time_str))
                log_print(datalog, '====================================================\n')
                log_print(datalog, 'Import the data from OK2Ship list...\n')
                
                ok2ship_data_link = self.ok2ship_data_path.get()
                self.OK2SHIP = TestData(pathdir = ok2ship_data_link, print_file_name=False)
                if len(self.OK2SHIP.value) == 0:
                    msgbox.showerror(title=None, message = 'No serial ID data could be found in the OK2ship list')
                    log_print(datalog, 'No serial ID data could be found in the OK2ship list! --- Program Terminated\n')
                else:
                    self.OK2SHIP.calc_retest()
                    log_print(datalog, '\n')
                    if self.OK2SHIP.retest_count > 0:
                        msgbox.showwarning(title='Repeating ID in Shipping list', 
                                           message= str(self.OK2SHIP.retest_count) +' parts are repeating parts!')
                        repeating_window = ErrorInfoList(desc_label='Repeating_parts')
                        repeating_window.input_text(self.OK2SHIP.retest_serial)
                        self.wait_window(repeating_window)
                        log_print(datalog, 'Some repeating serial IDs could be found in the ok2delivery list:')
                        for each_id in self.OK2SHIP.retest_serial:
                            log_print(datalog, each_id + '\n')
                    else:
                        log_print(datalog, 'All parts in ok2ship list are unique, no repeating parts\n')
                    log_print(datalog, '\n')
                    self.collect_comp_data()
                    self.checking_id_list = self.OK2SHIP.uni_serial
                    
                    for comp_data in self.compare_data_dict:
                        stage_issue_part_list = []
                        comp_name = str(comp_data['type'])
                        if len(str(comp_data['link'])) == 0:
                            log_print(datalog, 'No folder is defined for stage %s...\n' % comp_name)
                        else:
                            log_print(datalog, 'Import the data of stage %s from the folder %s ...\n' % (comp_name, str(comp_data['link'])))
                            Comp_RawData = TestData(str(comp_data['link']), print_file_name=False)
                            if len(Comp_RawData.value) == 0:
                                msgbox.showerror(title=None, message = 'No test data could be found in the folder of %s stage!' % comp_name)
                                log_print(datalog, 'No test data could be found in the folder of %s stage!\n' % comp_name)
                            else:
                                target_export_file = os.path.join(self.output_data_path.get(), comp_name+'.csv')
                                Comp_RawData.export_to_excel(target_export_file, "")
                                log_print(datalog, 'The data is exported to the %s in output folder\n' % target_export_file)
                                Comp_RawData.calc_retest()
                                log_print(datalog, 'In this stage, total %d test records.\n' % Comp_RawData.module_count)
                                log_print(datalog, 'Total pass parts count: %d \n' % Comp_RawData.pass_count)
                                log_print(datalog, 'Total retest parts count: %d \n\n' % Comp_RawData.retest_total_count)
                                allowed_retest = int(comp_data['retest'])

                                for single_id in self.checking_id_list:
                                    single_id = single_id.replace("'","")
                                    #print(Comp_RawData.last_result(single_id, return_value = 'time'))
                                    if not single_id in Comp_RawData.uni_serial:
                                        log_print(datalog,  '%s module is not in the parts list of stage %s!\n' % (str(single_id), comp_name))
                                        stage_issue_part_list.append(single_id)
                                    else:
                                        last_test_result = Comp_RawData.last_result(single_id)
                                        if last_test_result[0] == 'PASS' or last_test_result[0] == 'NA':
                                            test_times = last_test_result[2]
                                            if allowed_retest > 0 and test_times > allowed_retest:
                                                stage_issue_part_list.append(single_id)
                                                log_print(datalog, '%s test for %d times, exceeded the maximum test times allowed: %d\n' % (single_id, test_times, allowed_retest))
                                                test_log = last_test_result[3]
                                                test_time_result_log = zip(list(test_log['start_time']), list(test_log['test_result']))
                                                for single_test_log in test_time_result_log:
                                                    log_print(datalog, 'test time: %s, test result: %s\n' % (single_test_log[0], single_test_log[1]))
                                                log_print(datalog, '\n')
                                        else:
                                            stage_issue_part_list.append(single_id)
                                            log_print(datalog, "%s's test result is not PASS in stage %s!\n" % (str(single_id), comp_name))
                                            # log_print(datalog, 'Actual test result is "%s"\n\n' % last_test_result[0])
                                            test_log = last_test_result[3]
                                            test_time_result_log = zip(list(test_log['start_time']), list(test_log['test_result']))
                                            for single_test_log in test_time_result_log:
                                                log_print(datalog, 'test time: %s, test result: %s\n' % (single_test_log[0], single_test_log[1]))
                                            log_print(datalog, '\n')
                                    

                        log_print(datalog, 'Finish the analysis of the stage %s.\n' % comp_name)
                        log_print(datalog, '---------------------------------------------------\n\n')
        

        
if __name__ == '__main__':
    screener = shipScreener()
    screener.mainloop()