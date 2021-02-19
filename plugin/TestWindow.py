# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 06:58:54 2020

@author: zddan
"""

import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import END

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os



class PdTable(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    # 显示数据
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    # 显示行和列头
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.axes[0][col]
        return None


class TableWin(QDialog):
    def __init__(self, parent=None):
        super(TableWin, self).__init__(parent)
        self.table_view = QTableView()
        self.setupUI()

    def setupUI(self):
        self.Vbox = QVBoxLayout(self)
        self.description_lbl = QLabel(self)

        self.btn_widget = QWidget(self)
        self.btn_layout = QHBoxLayout(self.btn_widget)
        self.okbutton = QPushButton('OK', self)
        self.okbutton.clicked.connect(self.close)

        self.exportbutton = QPushButton('Export to csv', self)
        self.exportbutton.clicked.connect(self.export_table)

        self.btn_layout.addWidget(self.exportbutton)
        self.btn_layout.addWidget(self.okbutton)

        self.Vbox.addWidget(self.description_lbl)
        self.Vbox.addWidget(self.table_view)
        self.Vbox.addWidget(self.btn_widget)

    def description_text(self, desc_text):
        self.description_lbl.setText(desc_text)

    def export_table(self):
        target_name, _ = QFileDialog.getSaveFileName(self, 'Save to excel file', '', 'csv Files (*.csv)')
        if target_name == '':
            QMessageBox.warning(self, '', 'No export table name defined!')
        else:
            if not (os.path.splitext(target_name)[1] in ['.csv', '.CSV']):
                csv_target_name = target_name + '.csv'

            else:
                csv_target_name = target_name
            # print(self.raw_data.stat_sum)
            if len(self._df) > 0:
                self._df.to_csv(csv_target_name)
            else:
                QMessageBox.warning(self, 'No data', 'No table content is found')

    def show_pd_table(self, df):
        self._df = df
        table_content = PdTable(self._df)
        self.table_view.setModel(table_content)




class ErrorInfoList_PyQT5(QDialog):
    #close_signal = PYQT_SIGNAL()
    def __init__(self, parent=None):
        super(ErrorInfoList_PyQT5, self).__init__(parent)
        #self.setFixedSize(*size)
        self.setupUI()


    def setupUI(self):
        self.Vbox = QVBoxLayout(self)
        self.warning_lbl = QLabel(self)
        self.content = QTextEdit()
        self.okbutton = QPushButton('OK', self)
        self.okbutton.clicked.connect(self.close)
        self.copybutton = QPushButton('Copy to clipboard', self)
        self.copybutton.clicked.connect(self.copy_text)
        self.Vbox.addWidget(self.warning_lbl)
        self.Vbox.addWidget(self.content)
        self.Vbox.addWidget(self.copybutton)
        self.Vbox.addWidget(self.okbutton)

    def input_text(self, text_list):
        self.content.setPlainText('\n'.join(text_list))

    def description_text(self, desc_text):
        self.warning_lbl.setText(desc_text)

    def copy_text(self):
        clip = QApplication.clipboard()
        clip.setText(self.content.toPlainText())



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

if __name__ == '__main__':
   '''app = QApplication(sys.argv)

    main = ErrorInfoList_PyQT5()
    main.show()
    # main.center()

    sys.exit(app.exec_())'''
   import sys
   import pandas as pd

   app = QApplication(sys.argv)

   data = {'性别': ['男', '女', '女', '男', '男'],
           '姓名': ['小明', '小红', '小芳', '小强', '小美'],
           '年龄': [20, 21, 25, 24, 29]}
   df = pd.DataFrame(data, index=['No.1', 'No.2', 'No.3', 'No.4', 'No.5'],
                     columns=['姓名', '性别', '年龄', '职业'])

   model = PdTable(df)
   view = QTableView()
   view.setModel(model)
   view.setWindowTitle('Pandas')
   view.resize(410, 250)
   view.setAlternatingRowColors(True)
   view.show()

   sys.exit(app.exec_())
        

