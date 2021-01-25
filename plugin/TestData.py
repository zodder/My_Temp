# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 14:38:48 2020

@author: zddan
   
"""

import os
import pandas as pd
# import re
import numpy as np
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import csv
from tkinter import ttk

####### define the default columns names useed in the test data ############
serial_id = 'serial_id'
station_id = 'station'
fixture_id = 'fixture_id'
test_result = 'test_result'
pass_bin = 'PASS'
start_time = 'start_time'


############################################################################


def search_files_list(pathdir, suffix_list=[]):
    file_list = []
    for root, folders, files in os.walk(pathdir):
        if len(suffix_list) > 0:
            for file in files:
                if os.path.splitext(file)[1] in suffix_list:
                    file_list.append(os.path.join(root, file))
        else:
            for file in files:
                file_list.append(os.path.join(root, file))
    return file_list


def sort_dict(yield_dict, keep_count=7):
    new_dict = sorted(yield_dict.items(), key=lambda x: x[1], reverse=True)
    other_fail_rate = 0
    if len(new_dict) > 7:
        other_fail_rate = sum([x[1] for x in new_dict[6:]])
        new_dict = new_dict[:6]

    new_dict = dict(zip([x[0] for x in new_dict], [x[1] for x in new_dict]))
    if other_fail_rate > 0:
        new_dict['Others'] = other_fail_rate
    # print(new_dict)
    return new_dict


def open_data(folderpath, filename):
    start_line = [5, 0, 4, 6, 3, 2, 1]
    read_content = pd.DataFrame()
    feedback_code = 0
    for i in start_line:
        if os.path.splitext(filename)[1] in ['.CSV', '.csv']:
            # print('This is a csv file')
            try:
                read_content = pd.read_csv(os.path.join(folderpath, filename), header=i, index_col=False,
                                           low_memory=False)

            except:
                print('!!!!!!!!!!The data from ' + str(filename) + ' cannot be read rightly')
                feedback_code = 2

        elif os.path.splitext(filename)[1] in ['.xlsx', '.XLSX', '.xls', '.XLS']:
            # print('This is an xls file')
            try:
                read_content = pd.read_excel(os.path.join(folderpath, filename), header=i, index_col=False,
                                             low_memory=False)
            except:
                print('!!!!!!!!!!The data from ' + str(filename) + ' cannot be read rightly')
                feedback_code = 2
        else:
            pass

        if serial_id in read_content.columns:
            # print(str(filename))

            feedback_code = 1
            break
        else:
            read_content = pd.DataFrame()

    # print(read_data)
    return read_content, feedback_code


def resize(data_list):
    sum_data = np.array(data_list).sum()
    new_size = [x / sum_data for x in list(data_list)]
    return new_size


def read_spec(file_path):  # 从file的前面几行（2~5），首单元格名称一般为Errorcode, Upperlimit, Lowerlimit

    file_name = os.path.split(file_path)[1]
    head_content = []
    primary_spec = pd.DataFrame()

    if os.path.splitext(file_name)[1] in ['.CSV', '.csv']:
        with open(file_path, 'r') as csvdata:
            content_csv = csv.reader((line.replace('\0', '') for line in csvdata), delimiter=",")
            content_rows = [row for row in content_csv]
        head_content = content_rows[:5]
        try:
            primary_spec = pd.read_csv(file_path, header=1, nrows=4, index_col=False)
            # print(primary_spec.T)
        except:
            print('!!!!Cannot read the right spec data')
    elif os.path.splitext(file_name)[1] in ['.xlsx', '.XLSX', 'xls', '.XLS']:
        try:
            primary_spec = pd.read_excel(file_path, header=1, nrows=4, index_col=False)
        except:
            print('!!!!Cannot read the right spec data')
    if not primary_spec.empty:
        primary_spec = primary_spec.T
        primary_spec.set_axis(primary_spec.iloc[0], axis=1, inplace=True)
        primary_spec.columns.name = None
        if 'Upperlimit' in primary_spec.columns:
            primary_spec.drop(['Errorcode'], inplace=True)
            primary_spec.dropna(subset=['Upperlimit', 'Lowerlimit'], how='all', inplace=True)
            primary_spec.rename(columns={serial_id: 'item_name'}, inplace=True)
            # primary_spec.fillna(0)
        else:
            head_content = []
            primary_spec = pd.DataFrame()

        # primary_spec.columns = primary_spec

    return head_content, primary_spec


class SeriesData:
    def __init__(self, raw_data):
        self.value = np.array(raw_data)
        if len(self.value) > 0:
            self.min = np.min(self.value)
            self.max = np.max(self.value)
        else:
            self.min = self.max = np.nan
        self.count = len(self.value)
        self.sum = np.sum(self.value)
        self.hi_limit = self.lo_limit = 0
        # self.sumsqrs = np.sum([value*value for value in values])
        try:
            self.mean = np.mean(self.value) if self.count > 0 else None
        except:
            print(raw_data)
        self.median = np.median(self.value)

        # self.median = self.q2 = self.values[self.count/2]
        self.std = np.std(self.value, ddof=1)
        self.cpk = 'NA'
        self.cp = 0
        self.lo_failure_count = self.hi_failure_count = 0
        self.failure_count = 0

        self.dev_rate = 0

    def adapt_limit(self, Hi_limit, Lo_limit):

        self.hi_limit = Hi_limit
        self.lo_limit = Lo_limit

        if self.std == 0 or len(self.value) == 0:
            self.cpu = self.cpl = self.cp = self.cpk = 'Inf'
        else:

            self.cpu = np.nan if np.isnan(Hi_limit) else (Hi_limit - self.mean) / 3 / self.std
            self.cpl = np.nan if np.isnan(Lo_limit) else (self.mean - Lo_limit) / 3 / self.std

            if np.isnan(Hi_limit) and not np.isnan(Lo_limit):
                self.cp = self.cpk = self.cpl
                self.lo_failure_count = len(self.value[self.value < Lo_limit])
            elif np.isnan(Lo_limit) and not np.isnan(Hi_limit):
                self.cp = self.cpk = self.cpu
                self.hi_failure_count = len(self.value[self.value > Hi_limit])
            elif np.isnan(Hi_limit) and np.isnan(Lo_limit):
                self.cp = 'NA'
            else:
                self.hi_failure_count = len(self.value[self.value > Hi_limit])
                self.lo_failure_count = len(self.value[self.value < Lo_limit])
                self.cp = (Hi_limit - Lo_limit) / 6 / self.std
                self.cpk = min(self.cpu, self.cpl)

            self.failure_count = self.hi_failure_count + self.lo_failure_count


class TestData:
    def __init__(self, pathdir='',
                 raw_data=pd.DataFrame(),
                 ):
        self.value = pd.DataFrame()  # 数据源
        self.count = 0  # 数据数量
        self.yield_value = 0  #
        self.yield_df = pd.DataFrame()
        self.multi_yield_df = pd.DataFrame()
        self.read_file_list = []
        self.wrong_file_list = []
        self.missing_list = []
        self.spec = pd.DataFrame()
        self.head_rows = []
        self.stat_sum = pd.DataFrame()
        self.pass_count = 0
        self.retest_sum = pd.DataFrame()
        self.retest_pass_count = self.retest_total_count = self.retest_pass_count = self.retest_count = 0
        self.files_list = []
        self.files_count = 0

        if len(pathdir) > 0:
            self.read_data_from_files(pathdir=pathdir)
        elif len(raw_data) > 0:
            self.read_data_from_pd(raw_data=raw_data)

    def read_data_from_pd(self, raw_data, spec=pd.DataFrame(), head_rows=[]):
        if len(raw_data) > 0:
            self.value = raw_data
        if len(spec) > 0:
            self.spec = spec
        if len(head_rows) > 0:
            self.head_rows = head_rows

    def read_data_from_files(self, pathdir='', files_list=[], tk_pbar=(), ifPrintName=True):
        if os.path.isdir(pathdir):
            files_list = [file for file in search_files_list(pathdir, suffix_list=['.csv', '.CSV', '.xlsx', '.XLSX']) if
                          not file.startswith('~') or file.startswith('.')]
        elif os.path.isfile(pathdir):
            files_list = [pathdir]

        self.files_list = files_list
        self.files_count = len(files_list)

        if len(tk_pbar) > 0:
            if_tk_bar = isinstance(tk_pbar[1], ttk.Progressbar)
        else:
            if_tk_bar = False
        if if_tk_bar:
            root, bar = tk_pbar
            bar['maximum'] = self.files_count
            bar['value'] = 0

        if len(files_list) > 0:
            if len(self.spec) == 0:
                self.head_rows, self.spec = read_spec(files_list[0])
            for single_file in files_list:
                feedback_code = 0
                single_path = os.path.split(single_file)
                single_data, feedback_code = open_data(single_path[0], single_path[1])
                try:
                    self.value = pd.concat([self.value, single_data])
                except:
                    print('!!!!!!!!!!The data from ' + str(single_path[1]) +
                          ' cannot be merged correctly!')
                    feedback_code = 2
                if feedback_code == 1:
                    if ifPrintName:
                        print(single_path[1])
                    self.read_file_list.append(single_file)
                elif feedback_code == 2 or feedback_code == 0:
                    self.wrong_file_list.append(single_file)
                    print('The file ' + str(single_file) + ' cannot be read correctly')
                if if_tk_bar:
                    bar['value'] += 1
                    root.update()
        else:
            print('There is no files in the target folder...')
        if if_tk_bar:
            bar['value'] = 0
            root.update()

    def calc_parameters(self):
        self.count = len(self.value)  # data数量总记录
        if len(self.value) > 0:
            # 按照测试时间start_time升序排列
            if start_time in self.value.columns:
                self.value.sort_values(by=[start_time])
            else:
                print('No start time, so the data will not be sorted')

            # 将Serial id 全部转化为str格式，并且去除掉开始的'符号
            # 将serial_id 为空的行全部删除
            if serial_id in self.value.columns:
                self.value[serial_id] = self.value[serial_id].apply(str)
                self.value.dropna(subset=[serial_id], inplace=True)
                # 如果有station id， 把station id为空的行全部删除
                if station_id in self.value.columns:
                    self.value.dropna(subset=[station_id], inplace=True)
                # remove the ' from the serial_id
                self.value[serial_id] = self.value[serial_id].map(lambda x: str(x.replace("'", "")))

                self.serial = np.array(self.value[serial_id])
                self.uni_serial = np.unique(self.serial)
                self.uni_count = len(self.uni_serial)
                if test_result in self.value.columns:
                    self.pass_serial = np.unique(
                        np.array(self.value.loc[self.value[test_result] == pass_bin, serial_id]))
            else:
                print('No serial id in the data?')

            # 统计rawdata中是否含有station, fixture_ID, 并combine成唯一的fixture id
            self.station_id = np.unique(self.value[station_id]) if station_id in self.value.columns else np.array([])
            self.station_count = len(self.station_id)

            if fixture_id in self.value.columns:
                if station_id in self.value.columns:
                    # self.station_id = np.unique(self.value[station_id])
                    self.value['real_fixture_id'] = self.value[[station_id, fixture_id]].apply(
                        lambda x: str(x[station_id]) + '%' + str(x[fixture_id]), axis=1)
                else:
                    # self.station_id = np.array([])
                    self.value['real_fixture_id'] = self.value[fixture_id].apply(str)
                self.fixture_id = np.unique(self.value['real_fixture_id'])
            else:
                self.fixture_id = np.array([])
            self.fixture_count = len(self.fixture_id)

            '''
            # 如果有test_result字段，自动计算良率属性, 默认'PASS'(非'pass'！） 标记为good part
            if test_result in self.value.columns:
                self.calc_yield(yield_id=test_result, input_id=input_id)
            else:
                print('No test result in the data, so the yield cannot be calculated')
            '''

        else:
            print('No data has been really imported... \n')

    def __str__(self):
        if len(self.value) > 0:
            return str('Total ' + str(self.count) + ' parts are captured, with '
                       + str(self.pass_count) + ' parts can pass')
        else:
            return "No real value imported..."

    def __repr__(self):
        print(self.value)
        return str('Total ' + str(self.count) + ' parts are captured, with ' +
                   str(self.pass_count) + ' parts can pass')

    def __getitem__(self, index):
        return self.value.iloc[index]

    def __len__(self):
        return len(self.value)

    def __add__(self, second_data):
        result = TestData()
        result.read_data_from_pd(raw_data=pd.concat([self.value, second_data.value]), spec=self.spec,
                                 head_rows=self.head_rows)
        return result

    def check_id(self, sid):
        sid = sid.replace("'", "")
        if sid in self.uni_serial:
            return True
        else:
            return False

    def calc_yield(self, yield_id=test_result, input_id='Main'):

        if not self.spec.empty:
            self.calc_stat()

        if yield_id in self.value.columns:
            self.value[yield_id] = self.value[yield_id].fillna('NaN')
            self.test_results = dict(Counter(np.array(self.value[yield_id])))
            self.bin_name_list = list(self.test_results.keys())
            self.bin_count_list = list(self.test_results.values())
            if pass_bin in self.bin_name_list:
                self.pass_count = self.test_results[pass_bin]
            else:
                self.pass_count = 0

            if self.count != 0:
                self.yield_value = self.test_results[pass_bin] / self.count
            else:
                self.yield_value = 0
            self.module_count = sum(self.bin_count_list)
            self.fail_count = self.module_count - self.pass_count
            self.yield_list = [bin_count / self.module_count for bin_count in self.bin_count_list]

            self.yield_dict = dict(zip(self.bin_name_list, self.yield_list))
            self.fail_yield_dict = self.yield_dict.copy()
            if pass_bin in self.bin_name_list:
                self.fail_yield_dict.pop(pass_bin)
            self.fail_yield_dict = sort_dict(self.fail_yield_dict)

            self.yield_dict['TotalCount'] = self.count
            self.yield_dict['PassCount'] = self.pass_count
            self.yield_dict['FailCount'] = self.fail_count
            self.yield_df = pd.DataFrame(self.yield_dict, index=[input_id])
            self.multi_yield_df = self.yield_df

            # self.calc_fixture()
            # print('percent: {:.3%}'.format(self.yield_value))
            # print('total count: %d' % self.module_count)
        else:
            print('No ' + str(yield_id) + ' column in the raw data, cannot calculate the yield')

    def calc_fixture(self, fixture_id='real_fixture_id'):

        if self.station_count > 1:
            for single_station_id in self.station_id:
                single_raw_data = self.value.loc[self.value[station_id] == single_station_id].copy()
                single_data = TestData(raw_data=single_raw_data)
                single_data.calc_parameters()
                single_data.calc_yield(input_id=single_station_id)
                output_df = single_data.yield_df
                self.multi_yield_df = pd.concat([self.multi_yield_df, output_df])

        if self.fixture_count > 1:
            for single_fixture_id in self.fixture_id:
                single_raw_data = self.value.loc[self.value[fixture_id] == single_fixture_id].copy()
                single_data = TestData(raw_data=single_raw_data)
                single_data.calc_parameters()
                single_data.calc_yield(input_id=single_fixture_id)
                output_df = single_data.yield_df
                self.multi_yield_df = pd.concat([self.multi_yield_df, output_df])

    def screen(self, remove_retest=True, inplace=False, how='last'):
        '''
        if how == 'last': keep the last test result for retest parts as yield
        if how == 'first': keep the first test result for retest parts
       
        '''
        screened_data = self.value.copy()
        if remove_retest and how == 'last':
            screened_data.drop_duplicates(subset=serial_id, keep='last', inplace=True)
        elif remove_retest and how == 'first':
            screened_data.drop_duplicates(subset=serial_id, keep='first', inplace=True)

        if inplace:
            self.value = screened_data
            self.calc_yield()
        return screened_data

    def last_result(self, target_id):
        '''
        Parameters
        ----------
        target_id : TYPE
            DESCRIPTION.

        Returns
        -------
        return the result of a single serial ID, which contains below information

        '''

        target_id = target_id.replace("'", "")
        test_results = self.value.loc[self.value[serial_id] == target_id].copy()
        last_result = test_results.drop_duplicates(subset=serial_id, keep='last')
        test_times = len(test_results)
        return_results = []

        if test_result in last_result.columns and test_times > 0:
            last_test_result = str(last_result[test_result].values[0])
        else:
            last_test_result = 'NA'
        return_results.append(last_test_result)
        if start_time in last_result.columns and test_times > 0:
            last_test_time = str(last_result[start_time].values[0])
        else:
            last_test_time = 'NA'
        return_results.append(last_test_time)
        return_results.append(test_times)
        return_results.append(test_results[[start_time, test_result]])

        return return_results

    def search_id(self, target_list, inplace=True):
        self.value['iffind'] = ''
        self.missing_list = []
        target_list = [a.replace("'", "") for a in target_list]
        # print(target_list)

        for single_id in target_list:
            if single_id in self.uni_serial:
                self.value.loc[self.value[serial_id] == single_id, 'iffind'] = 'YES'

            else:
                self.missing_list.append(single_id)

        # print(missing_list)
        if inplace:
            self.value = self.value.loc[self.value['iffind'] == 'YES']
            # self.value.drop(self.value[self.value['iffind'] !='YES'].index, inplace=True)
            self.calc_yield()
            # self.missing_list = missing_list
        # else:
        #    return self.value.loc[self.value['iffind'] == 'YES'], missing_list

    def calc_retest(self):
        # serial_dict = { serial_id: self.uni_serial }
        self.retest_sum = pd.DataFrame(
            {serial_id: self.uni_serial})  # generate a new dataframe with uni_serial id in the list
        self.retest_sum['Test_times'] = 0
        retest_count = Counter(np.array(self.value[serial_id]))  # calculate the test count of each id
        self.retest_sum['Test_times'] = self.retest_sum[serial_id].apply(lambda x: retest_count[x])
        self.retest_sum.drop(self.retest_sum[self.retest_sum['Test_times'] < 2].index, inplace=True)
        self.retest_count = len(self.retest_sum)
        self.retest_sum['Retest_results'] = self.retest_sum[serial_id].apply(lambda x: self.retest_word(x))
        self.retest_sum['Retest_yield'] = self.retest_sum['Retest_results'].apply(
            lambda x: format(x.count('P') / len(x), '.2%'))
        self.retest_sum['Final_result'] = self.retest_sum['Retest_results'].apply(lambda x: x[-1])
        self.retest_pass_count = list(self.retest_sum['Final_result']).count('P')
        self.retest_total_count = len(self.retest_sum['Final_result'])
        if self.retest_total_count > 0:
            self.retest_pass_rate = self.retest_pass_count / self.retest_total_count
        else:
            self.retest_pass_rate = 0
        self.retest_serial = np.unique(self.retest_sum[serial_id])

    def retest_word(self, module_id):
        word = ''
        module_result = self.value[self.value[serial_id] == module_id]
        module_result.sort_values(by=[start_time])
        for i in range(len(module_result)):
            single_result = module_result.iloc[i]
            if single_result[test_result] == pass_bin:
                word += 'P'
            else:
                word += 'X'
        return word

    def export_to_excel(self, target_csv_name, target_sum_name):
        drop_columns = []

        if 'real_fixture_id' in self.value.columns:
            drop_columns.append('real_fixture_id')
        if 'iffind' in self.value.columns:
            drop_columns.append('iffind')

        if len(target_csv_name) > 0:
            if len(drop_columns) > 0:
                export_data = self.value.drop(drop_columns, axis=1, inplace=False)
            export_data[serial_id] = export_data[serial_id].apply(lambda x: "'" + str(x.replace("'", "")))
            if self.spec.empty:
                export_data.to_csv(target_csv_name, index=False)
            else:
                f_temp = os.path.splitext(target_csv_name)[0] + '_temp.csv'
                export_data.to_csv(f_temp, index=False)
                with open(f_temp, 'r') as data_csv:
                    data_result = csv.reader(data_csv)
                    data_csv_line = [line for line in data_result]
                with open(target_csv_name, "w", newline='') as final_csv:  # not defined: encoding='utf-8'
                    csv_writer = csv.writer(final_csv)
                    for row_1 in self.head_rows:
                        csv_writer.writerow(row_1)
                    for row_2 in data_csv_line:
                        csv_writer.writerow(row_2)
                os.remove(f_temp)

        if len(target_sum_name) > 0:
            with pd.ExcelWriter(target_sum_name) as Excel_writer:

                # export_data.to_excel(Excel_writer, 'total_data', index=False)
                self.multi_yield_df.to_excel(Excel_writer, 'Yield_Summary', index=True)
                if len(self.missing_list) > 0:
                    self.missing_df = pd.DataFrame(self.missing_list, columns=['Missing_ID'])
                    self.missing_df.to_excel(Excel_writer, 'ID_cannot_be_found', index=False)
                # if len(self.stat_sum) > 0:
                print('summary:')
                print(self.stat_sum)
                self.stat_sum.to_excel(Excel_writer, 'Data_Summary', index=False)
                if len(self.retest_sum) > 0:
                    self.retest_sum.to_excel(Excel_writer, 'Retest_Summary', index=False)

    def calc_stat(self):
        self.stat_sum = pd.DataFrame()
        if not self.spec.empty:
            for i in range(len(self.spec)):
                item = self.spec.iloc[i]

                item_name = item['item_name']
                item_unit = item['Units']
                item_upper_limit = item['Upperlimit']
                item_lower_limit = item['Lowerlimit']

                raw_data = np.array(self.value[item_name].dropna())

                if np.issubdtype(raw_data.dtype, np.number):
                    item_data = SeriesData(raw_data)
                    item_upper_limit = np.nan if pd.isnull(item_upper_limit) else float(item_upper_limit)
                    item_lower_limit = np.nan if pd.isnull(item_lower_limit) else float(item_lower_limit)

                    item_data.adapt_limit(Hi_limit=item_upper_limit, Lo_limit=item_lower_limit)
                    single_row = pd.DataFrame(
                        data=[[item_name, item_upper_limit, item_lower_limit, item_unit, item_data.count,
                               item_data.max, item_data.min, item_data.mean, item_data.median,
                               item_data.std, item_data.cp, item_data.cpk, item_data.failure_count]],
                        columns=['ItemName', 'UpperLimit', 'LowerLimit', 'Unit', 'Count', 'Max', 'Min',
                                 'Average', 'Median', 'Stdev', 'Cp', 'CpK', 'FailureCount'])
                    self.stat_sum = pd.concat([self.stat_sum, single_row])


class DataFigure:
    def __init__(self, figsize=(6, 6), dpi=60, axsize=[0.1, 0.1, 0.95, 0.95]):
        # self.fig, self.ax = plt.subplots(figsize = (18, 9))
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self.ax = plt.axes(axsize)

    def set_title(self, title_name, fontsize=20, fontweight='bold'):
        self.ax.set_title(title_name, fontsize=fontsize, fontweight=fontweight)

    def ring(self, input_data, autopct):
        labels = list(input_data.keys())
        data_values = np.array(input_data.values())
        # sum_data = sum(data_values)
        data_size = resize(data_values)
        self.ax.pie(x=data_size, labels=labels, autopct=autopct)
        self.ax.pie(radius=0.55, x=[1], colors='white')

    def pareto_bar(self, input_data):
        bin_names = list(input_data.keys())
        bin_value = list(input_data.values())
        sns.barplot(x=bin_names, y=bin_value, alpha=0.7, ax=self.ax)
        for i in range(len(bin_names)):
            self.ax.text(x=i - 0.25, y=bin_value[i], s="%.2f%%" % (bin_value[i] * 100), c='black', fontsize=15)
        for tick in self.ax.get_xticklabels():
            tick.set_rotation(90)

    def hist_bar(self, input_data, range, bins):
        self.ax.hist(x=input_data, range=range, bins=bins)

    def yield_bar(self, input_data):
        bin_names = list(input_data.keys())
        bin_value = list(input_data.values())
        self.ax.barh(y=range(len(bin_names)), tick_label=bin_names, width=bin_value, height=0.65, facecolor='green')
        for i in range(len(bin_names)):
            self.ax.text(x=bin_value[i] * 0.5 * 0.9, y=i, s="%.2f%%" % (bin_value[i] * 100), c='white', fontsize=15)

        self.ax.set_xlim(0, 1)
        self.ax.set_xticks([])
        # self.ax.set_ylim(0, 8)
        # for tick in self.ax.get_yticklabels():
        #    tick.set_rotation(90)
