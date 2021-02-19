# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from collections import Counter
import time
import os
import random
import csv
from plugin.TestData import SeriesData


def search_files_list(pathdir, suffix_list=[], walkinfolder=True):
    file_list = []
    if walkinfolder:
        for root, folders, files in os.walk(pathdir):
            if len(suffix_list) > 0:
                for file in files:
                    if os.path.splitext(file)[1] in suffix_list:
                        file_list.append(os.path.join(root, file))
            else:
                for file in files:
                    file_list.append(os.path.join(root, file))
        return file_list
    else:
        file_list = [file for file in os.listdir(pathdir)]
        if len(suffix_list) > 0:
            file_list = [file for file in file_list if os.path.splitext(os.path.split(file)[1])[1] in suffix_list]
        return file_list


def sort_yield_dict(yield_dict, keep_count=7):
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


def spec_pd2dict(spec_df):
    new_dict = {}
    for index, row in spec_df.iterrows():
        itemname = row['Item_name']
        upperlimit = row['Upperlimit'] if not pd.isnull(row['Upperlimit']) else np.nan
        lowerlimit = row['Lowerlimit'] if not pd.isnull(row['Upperlimit']) else np.nan
        unit = row['Units'] if not pd.isnull(row['Units']) else np.nan
        if isinstance(itemname, str):
            new_dict[itemname] = {'Upperlimit': upperlimit, 'Lowerlimit': lowerlimit, 'Units': unit}

    return new_dict


class TestData:
    def __init__(self):
        self.value = pd.DataFrame()
        self.identical_id = ''
        self.time_id = ''
        self.headers_list = [0]
        self.iflog = True  # define if the log should be shown in the list

        self.read_files_list = []
        self.wrong_files_list = []
        self.spec = {}
        self.statistic_summary = pd.DataFrame()

        self.quantity = 0

    def read_from_pd(self, raw_data=pd.DataFrame()):
        if len(raw_data) > 0:
            self.value = raw_data

    def read_from_csv(self, filepath='', header=0):
        if len(filepath) > 0:
            self.value = pd.read_csv(filepath, low_memory=False, header=header)
            self.read_files_list.append(filepath)

    def read_from_folder(self, pathdir):
        files_list = search_files_list(pathdir, suffix_list=['.csv', '.CSV'])
        self.read_from_files(files_list=files_list)

    def read_from_files(self, files_list, exemptionfilelist=[]):
        print('self id is %s' % self.identical_id)
        read_content = []
        for i, file in enumerate(files_list):
            if file not in exemptionfilelist:
                for header in self.headers_list:
                    try:
                        errorcode = 0
                        data = pd.read_csv(file, low_memory=False, header=header, index_col=False)
                    except UnicodeDecodeError:
                        print('%d - File of %s cannot be read rightly because of unicode decode issue' % (i, file))
                        errorcode = 1
                        self.wrong_files_list.append(file)

                    except Exception as err:
                        print('%s Failed type is: %s' % (file, err.__class__.__name__))
                        print('Failed detail information is:', err)
                        errorcode = 2
                    else:
                        if len(self.identical_id) > 0 and self.identical_id in data.columns \
                                or len(self.identical_id) == 0:
                            data.dropna(how='all', inplace=True)
                            break
                        else:
                            errorcode = 3

                if errorcode == 0:
                    read_content.append(data)
                    if self.iflog:
                        strtime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                        filesize = os.path.getsize(file) / 1024
                        print('%d - Finish file data read of %s (size: %d k) at %s' % (i, file, filesize, strtime))
                    self.read_files_list.append(file)
                else:
                    self.wrong_files_list.append(file)

        if len(read_content) > 0:
            self.value = pd.concat([self.value] + read_content)
        if self.iflog:
            strtime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print('Finish file data merge at %s' % strtime)

    def __len__(self):
        return len(self.value)

    def __str__(self):
        if len(self.value) > 0:
            return str('Total %d parts are captured' % len(self.value))
        else:
            return "No real value loaded..."

    def __getitem__(self, index):
        return self.value.iloc[index]

    def calc_statistic_summary(self):
        if len(self.spec) > 0:
            for item_name in self.spec.keys():
                item_units = self.spec[item_name]['Units']
                item_upperlimit = self.spec[item_name]['Upperlimit']
                item_lowerlimit = self.spec[item_name]['Lowerlimit']

                raw_data = np.array(self.value[item_name].dropna())

                if np.issubdtype(raw_data.dtype, np.number):
                    item_data = SeriesData(raw_data)
                    try:
                        item_upperlimit = float(item_upperlimit)
                    except ValueError:
                        item_upperlimit = np.nan
                    try:
                        item_lowerlimit = float(item_lowerlimit)
                    except ValueError:
                        item_lowerlimit = np.nan

                    item_data.adapt_limit(Hi_limit=item_upperlimit, Lo_limit=item_lowerlimit)
                    single_row = pd.DataFrame(
                        data=[[item_name, item_upperlimit, item_lowerlimit, item_units, item_data.count,
                               item_data.max, item_data.min, item_data.mean, item_data.median,
                               item_data.std, item_data.cp, item_data.cpk, item_data.failure_count]],
                        columns=['ItemName', 'UpperLimit', 'LowerLimit', 'Unit', 'Count', 'Max', 'Min',
                                 'Average', 'Median', 'Stdev', 'Cp', 'CpK', 'FailureCount'])
                    self.statistic_summary = pd.concat([self.statistic_summary, single_row])

    def to_csv(self, *args, **kwargs):
        if len(self.value) > 0:
            self.value.to_csv(*args, **kwargs)
        else:
            print('No real value imported, cannot export to external csv file')


class CameraData(TestData):

    def __init__(self, pathdir=''):
        super(CameraData, self).__init__()
        self.identical_id = 'serial_id'

        self.time_id = 'start_time'
        self.pass_id = 'PASS'
        self.station_id = 'station'
        self.test_result_id = 'test_result'
        self.fixture_id = 'fixture_id'

        self.time_format = '%Y%m%d_%H%M%S'

        self.headers_list = [5, 0]

        self.uni_serial = np.array([])
        self.uni_serial_qty = 0
        self.station_list = np.array([])
        self.station_qty = 0
        self.fixture_list = np.array([])
        self.fixture_qty = 0
        self.pass_count = self.fail_count = self.yield_value = 0
        self.bin_results = self.yield_dict = self.fail_yield_dict = {}
        self.yield_df = self.multi_yield_df = self.retest_sum = pd.DataFrame()
        self.head_rows = []

        if len(pathdir) > 0:
            if os.path.isdir(pathdir):
                self.read_from_folder(pathdir)
            elif os.path.isfile(pathdir):
                self.read_from_files([pathdir])

    def cleanup(self):
        self.value.drop_duplicates(keep='first', inplace=True)
        self.quantity = len(self.value)  # quantity of all the records
        if len(self.value) > 0:
            # sort the records by the time
            self.read_spec()
            if self.time_id in self.value.columns:
                self.value.sort_values(by=[self.time_id], inplace=True)
            else:
                print('No start time, so the data will not be sorted')

            if self.identical_id in self.value.columns:
                self.value[self.identical_id] = self.value[self.identical_id].apply(str)
                # self.value.dropna(subset=[self.identical_id], inplace=True)
                # if self.identical_id in self.value.columns:
                #    self.value.dropna(subset=[station_id], inplace=True)

                # remove the ' from the serial_id
                self.value[self.identical_id] = self.value[self.identical_id].map(lambda x: str(x.replace("'", "")))

                _serial_list = np.array(self.value[self.identical_id])
                self.uni_serial = np.unique(_serial_list)
                self.uni_serial_qty = len(self.uni_serial)
                # if self.test_result_id in self.value.columns:
                #    self.pass_serial = np.unique(
                #        np.array(self.value.loc[self.value[test_result] == pass_bin, serial_id]))
            else:
                print('No identical id in the data, cannot distinguish the records')

            # 统计rawdata中是否含有station, fixture_ID, 并combine成唯一的fixture id
            self.station_list = np.unique(
                self.value[self.station_id]) if self.station_id in self.value.columns else np.array([])
            self.station_qty = len(self.station_list)

            if self.fixture_id in self.value.columns:
                if self.station_id in self.value.columns:
                    # self.station_id = np.unique(self.value[station_id])
                    self.value['real_fixture_id'] = self.value[[self.station_id, self.fixture_id]].apply(
                        lambda x: str(x[self.station_id]) + '%' + str(x[self.fixture_id]), axis=1)
                else:
                    self.value['real_fixture_id'] = self.value[self.fixture_id].apply(str)
                self.fixture_list = np.unique(self.value['real_fixture_id'])
            else:
                self.fixture_list = np.array([])
            self.fixture_qty = len(self.fixture_id)

        else:
            print('No data has been really imported... \n')

    def calc_yield(self, input_id='Overall'):

        if len(self.spec) > 0:
            self.calc_statistic_summary()

        if self.test_result_id in self.value.columns and self.quantity > 0:
            self.value[self.test_result_id] = self.value[self.test_result_id].fillna('NaN')
            self.bin_results = dict(Counter(np.array(self.value[self.test_result_id])))
            # self.bin_name_list = list(self.bin_results.keys())
            # self.bin_count_list = list(self.bin_results.values())
            if self.pass_id in self.bin_results.keys():
                self.pass_count = self.bin_results[self.pass_id]
                self.yield_value = self.pass_count / self.quantity
            else:
                self.pass_count = self.yield_value = 0

            self.fail_count = self.quantity - self.pass_count
            yield_list = [bin_count / self.quantity for bin_count in self.bin_results.values()]

            self.yield_dict = dict(zip(self.bin_results.keys(), yield_list))
            self.fail_yield_dict = self.yield_dict.copy()
            if self.pass_id in self.bin_results.keys():
                self.fail_yield_dict.pop(self.pass_id)
            self.fail_yield_dict = sort_yield_dict(self.fail_yield_dict)

            self.yield_dict['TotalCount'] = self.quantity
            self.yield_dict['PassCount'] = self.pass_count
            self.yield_dict['FailCount'] = self.fail_count
            self.yield_df = pd.DataFrame(self.yield_dict, index=[input_id])
            self.multi_yield_df = pd.concat([self.multi_yield_df, self.yield_df])
        else:
            print('No ' + str(self.pass_id) + ' column in the raw data, cannot calculate the yield')

    def reorganize(self, input_id='Overall'):
        self.multi_yield_df = pd.DataFrame()
        self.cleanup()
        self.calc_yield(input_id=input_id)
        self.calc_statistic_summary()

    def __copy__(self):
        new_class = CameraData()
        new_class.read_from_pd(raw_data=self.value)
        new_class.spec = self.spec
        new_class.head_rows = self.head_rows
        return new_class

    def calc_fixture(self, fixture_id='real_fixture_id'):
        station_class = [self.station_qty, self.station_id, self.station_list]
        fixture_class = [self.fixture_qty, fixture_id, self.fixture_list]
        classification_list = [station_class, fixture_class]
        for single_class in classification_list:
            if single_class[0] > 1:
                for single_id in single_class[2]:
                    single_raw_data = self.value.loc[self.value[single_class[1]] == single_id].copy()
                    single_data = CameraData()
                    single_data.read_from_pd(raw_data=single_raw_data)
                    single_data.reorganize(input_id=single_id)
                    output_df = single_data.yield_df
                    self.multi_yield_df = pd.concat([self.multi_yield_df, output_df])

    def remove_retest(self, inplace=True, how='last'):
        # remove the retest value of the raw data, 'last' means Fpy, 'first' means fisrt pass yield
        if len(self) > 0:
            if inplace:
                self.value.drop_duplicates(subset=[self.identical_id], inplace=True, keep=how)
                self.reorganize()
            else:
                return self.value.drop_duplicates(subset=[self.identical_id], keep=how)

    def calc_retest(self):
        # serial_dict = { serial_id: self.uni_serial }
        # generate a new dataframe with uni_serial id in the list
        self.retest_sum = pd.DataFrame({self.identical_id: self.uni_serial})
        self.retest_sum['Test_times'] = 0
        retest_count = Counter(np.array(self.value[self.identical_id]))  # calculate the test count of each id
        self.retest_sum['Test_times'] = self.retest_sum[self.identical_id].apply(lambda x: retest_count[x])
        self.retest_sum.drop(self.retest_sum[self.retest_sum['Test_times'] < 2].index, inplace=True)
        # self.retest_count = len(self.retest_sum)
        self.retest_sum['Retest_results'] = self.retest_sum[self.identical_id].apply(lambda x: self.retest_word(x))
        self.retest_sum['Retest_yield'] = self.retest_sum['Retest_results'].apply(
            lambda x: format(x.count('P') / len(x), '.2%'))
        self.retest_sum['Final_result'] = self.retest_sum['Retest_results'].apply(lambda x: x[-1])
        # self.retest_pass_count = list(self.retest_sum['Final_result']).count('P')
        # self.retest_total_count = len(self.retest_sum['Final_result'])
        # if self.retest_total_count > 0:
        #    self.retest_pass_rate = self.retest_pass_count / self.retest_total_count
        # else:
        #    self.retest_pass_rate = 0
        # self.retest_serial = np.unique(self.retest_sum[self.identical_id])

    def retest_word(self, module_id):
        word = ''
        module_result = self.value[self.value[self.identical_id] == module_id]
        module_result.sort_values(by=[self.time_id])
        for i in range(len(module_result)):
            single_result = module_result.iloc[i]
            if single_result[self.test_result_id] == self.pass_id:
                word += 'P'
            else:
                word += 'X'
        return word

    def export_to_csv(self, target_csv_name):
        drop_columns = []

        if 'real_fixture_id' in self.value.columns:
            drop_columns.append('real_fixture_id')

        if len(target_csv_name) > 0:
            if len(drop_columns) > 0:
                export_data = self.value.drop(drop_columns, axis=1, inplace=False)
            export_data[self.identical_id] = export_data[self.identical_id].apply(
                lambda x: "'" + str(x.replace("'", "")))
            if len(self.head_rows) > 0:
                export_data.to_csv(target_csv_name, index=False)
            else:
                f_temp = os.path.splitext(target_csv_name)[0] + '_temp.csv'
                export_data.to_csv(f_temp, index=False)
                with open(f_temp, 'r') as data_csv:  # read the temperory exported csv file
                    data_result = csv.reader(data_csv)
                    data_csv_line = [line for line in data_result]
                with open(target_csv_name, "w", newline='') as final_csv:  # not defined: encoding='utf-8'
                    csv_writer = csv.writer(final_csv)
                    for row_1 in self.head_rows:
                        csv_writer.writerow(row_1)
                    for row_2 in data_csv_line:
                        csv_writer.writerow(row_2)
                os.remove(f_temp)

    def read_spec(self):  # 从file的前面几行（2~5），首单元格名称一般为Errorcode, Upperlimit, Lowerlimit
        if len(self.read_files_list) > 0:
            sample_file = self.read_files_list[random.choice(range(len(self.read_files_list)))]
            head_content = []
            primary_spec = pd.DataFrame()
            if os.path.splitext(sample_file)[1] in ['.CSV', '.csv']:
                with open(sample_file, 'r') as csvdata:
                    content_csv = csv.reader((line.replace('\0', '') for line in csvdata), delimiter=",")
                    content_rows = [row for row in content_csv]
                if self.identical_id in content_rows[5]:
                    self.head_rows = content_rows[:5]
                    try:
                        primary_spec = pd.read_csv(sample_file, header=1, nrows=4, index_col=False)
                    except:
                        print('!!!!Cannot read the right spec data')
                    else:
                        if not primary_spec.empty:
                            primary_spec = primary_spec.T
                            primary_spec.set_axis(primary_spec.iloc[0], axis=1, inplace=True)
                            primary_spec.columns.name = None
                            if 'Upperlimit' in primary_spec.columns:
                                primary_spec.drop(['Errorcode'], inplace=True)
                                primary_spec.dropna(subset=['Upperlimit', 'Lowerlimit'], how='all', inplace=True)
                                primary_spec.rename(columns={self.identical_id: 'Item_name'}, inplace=True)
                                self.spec = spec_pd2dict(primary_spec)

    def track_id_result(self, target_id):
        result_found = {}
        target_id = str(target_id).replace("'", "")  # remove potential ' in the id

        test_results = self.value.loc[self.value[self.identical_id] == target_id].copy()
        if self.time_id in test_results.columns:
            test_results.sort_values(by=[self.time_id], ascending=False)

        test_times = len(test_results)
        last_result = test_results.drop_duplicates(subset=self.identical_id, keep='last')

        if self.test_result_id in last_result.columns and test_times > 0:
            last_test_result = str(last_result[self.test_result_id].values[0])
        else:
            last_test_result = 'NA'

        result_found['Last_result'] = last_test_result

        if self.time_id in last_result.columns and test_times > 0:
            last_test_time = str(last_result[self.time_id].values[0])
        else:
            last_test_time = 'NA'

        result_found['Last_test_time'] = last_test_time
        result_found['Test_times'] = test_times
        if self.time_id in test_results.columns and self.test_result_id in test_results.columns:
            result_found['Test_history'] = test_results[[self.time_id, self.test_result_id]]
        else:
            result_found['Test_history'] = pd.DataFrame()

        return result_found

    def search_ids(self, target_list, inplace=True):
        target_list = [single_id.replace("'", "") for single_id in target_list]
        found_df = self.value.loc[self.value[self.identical_id].isin(target_list)]

        if inplace:
            self.value = found_df
            self.reorganize()
        else:
            return found_df



