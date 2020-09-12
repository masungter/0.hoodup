# -*- coding: utf-8 -*-

import sys, UI
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import *


ADD_DB = 'hood_up_db.csv'

class MainDialog(QDialog, UI.Ui_Dialog):
    def __init__(self):
        QDialog.__init__(self, None)
        self.setupUi(self)

        self.pushButton_1.clicked.connect(self.Input_BTN_clicked)
        self.pushButton_2.clicked.connect(self.clear_BTN_clicked)
        self.pushButton_3.clicked.connect(self.load_BTN_clicked)
        self.pushButton_4.clicked.connect(self.cal_BTN_clicked)
        self.pushButton_5.clicked.connect(self.Graph_1)
        self.pushButton_5.clicked.connect(self.Graph_2)

    def setTableWidgetData(self):
        # 향후 업데이트필요 사항
        #self.df['뺄값'] = 0
        #self.df['더할값'] = 0

        #엑셀 불러온 df 그래프로 표현
        self.tableWidget.setColumnCount(len(self.df.columns))
        self.tableWidget.setRowCount(len(self.df.index))

        col_head = self.df.columns
        print(col_head)

        self.tableWidget.setHorizontalHeaderLabels(col_head)

        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))



    def Input_BTN_clicked(self):

        ### 변수설정
        self.model = self.lineEdit_model.text()
        self.height = self.lineEdit_height.text()
        self.weight = self.lineEdit_weight.text()
        self.hinge_t = self.lineEdit_hinget.text()
        self.hinge_h = self.lineEdit_hingeh.text()
        self.hood_t = self.lineEdit_hoodt.text()
        self.hood_h = self.lineEdit_hoodh.text()
        self.factory = self.lineEdit_factory.text()
        self.uph = self.lineEdit_uph.text()
        self.pitch = self.lineEdit_pitch.text()
        self.degree = self.lineEdit_degree.text()

        text = '차종 : ' + self.model + ', 높이 : ' + self.height +  ', 무게 : ' + self.weight + 'kg \n'\
               +' 힌지축좌표 : ' + self.hinge_t + 'T / ' + self.hinge_h + 'H, 후드무게중심 '+ self.hood_t + 'T / ' + self.hood_h + 'H \n'\
               + '공장 : ' + self.factory + ', UPH : ' + self.uph + ', 피치 : ' + self.pitch + ', 입조각도 : ' + self.degree
        print(self.model, self.height)

        existline_textEdit = self.textEdit.toPlainText()
        self.textEdit.setText(existline_textEdit + text)

    def clear_BTN_clicked(self):
        self.textEdit.setText('')

    def load_BTN_clicked(self):
        ###  csv 표로 불러오기
        self.df = pd.read_csv(ADD_DB, encoding='cp949')
        self.setTableWidgetData()

    def cal_BTN_clicked(self):

        ### 변수설정
        self.height = float(self.lineEdit_height.text())
        self.weight = float(self.lineEdit_weight.text())
        self.hinge_t = float(self.lineEdit_hinget.text())
        self.hinge_h = float(self.lineEdit_hingeh.text())
        self.hood_t = float(self.lineEdit_hoodt.text())
        self.hood_h = float(self.lineEdit_hoodh.text())
        self.uph = float(self.lineEdit_uph.text())
        self.pitch = float(self.lineEdit_pitch.text())
        self.degree = float(self.lineEdit_degree.text())


        ### 계산 항목
        self.diff_t = self.hinge_t - self.hood_t
        self.diff_h = self.hinge_h - self.hood_h
        self.degree1 = self.diff_t / (self.diff_t ** 2 + self.diff_h ** 2) ** 0.5
        self.weight_h = - self.weight * self.degree1
        self.a = ((self.diff_t / 1000) ** 2 + (self.diff_h / 1000) ** 2) ** 0.5
        self.cos = np.cos(self.degree * 3.141592 / 180)
        self.con_v = self.uph * self.pitch / 3600
        self.con_h = self.con_v * np.sin(self.degree * 3.141592 / 180)
        self.density = 1050
        self.move_per1 = self.height / self.con_h / 1000

        ### 값 리셋
        self.df['cal_h'] = 2.5
        self.df['cal_velo'] = 0
        self.df['cal_q'] = 0
        self.df['cal_vol'] = 0
        self.df['cal_c_sum'] = 0
        self.df['cal_water'] = 0
        self.df['degree_2'] = abs(-1)
        self.df['sec'] = 0
        self.df['b_force'] = 0
        self.df['w_force'] = 0
        self.df['total_force'] = 0


        # 리얼계산

        self.temp = 0
        self.df.iloc[0, 6] = 0.221472345904

        for i in range(1, len(self.df.index)):

            # print(df.iloc[i,0])

            # cal_h 계산
            if (self.df.iloc[i, 0] - self.df.iloc[i - 1, 10]) < 0:
                self.df.iloc[i, 5] = 0
            else:
                self.df.iloc[i, 5] = 5 * (self.df.iloc[i, 0] - self.df.iloc[i - 1, 10]) / 2

            # cal_velo 계산
            self.df.iloc[i, 6] = (2 * 9.81 * self.df.iloc[i, 5] / 1000) ** 0.5

            # cal_q 계산
            self.df.iloc[i, 7] = self.df.iloc[i, 4] * self.df.iloc[i, 6] * 100

            # cal_vol 계산
            self.df.iloc[i, 8] = self.df.iloc[i, 7] * self.move_per1

            # cal_c_sum 계산
            self.temp += self.df.iloc[i, 8]
            self.temp_2 = self.df.iloc[i, 1]
            if self.temp > self.temp_2:
                self.df.iloc[i, 9] = self.temp_2
            else:
                self.df.iloc[i, 9] = self.temp

            # cal_water 계산
            self.count = 0
            for m in range(0, len(self.df.index)):
                if self.df.iloc[m, 1] <= self.df.iloc[i, 9]:
                    self.count += 1

            self.df.iloc[i, 10] = self.count

        #######################################
        self.df['degree_2'] = abs(self.df['T'] / (self.df['T'] ** 2 + self.df['H'] ** 2) ** 0.5)
        self.df['sec'] = self.df['no'] * self.move_per1
        self.df['b_force'] = self.density * (self.df['volume'] - self.df['cal_c_sum']) / 1000000 * self.df['degree_2']
        self.df['w_force'] = self.weight_h * self.a
        self.df['total_force'] = self.df['b_force'] + self.df['w_force']

        ### 그래프 불러오기
        self.setTableWidgetData()


    def Graph_1(self):
        width =0.07
        fig = plt.Figure()
        ax = fig.add_subplot(111)

        ax.bar(self.df['sec'], self.df['b_force'], width, label ='buoyancy', color = '#ffc000')
        ax.bar(self.df['sec'], self.df['w_force'], width, label ='gravity', color = '#9bbb59')
        ax.plot(self.df['sec'], self.df['total_force'], label ='sum', color = '#0000ff')
        ax.legend()

        canvas = FigureCanvas(fig)
        canvas.draw()

        self.horizontalLayout_3.addWidget(canvas)

        canvas.show()

    def Graph_2(self):
        width = 0.07
        fig = plt.Figure()
        ax = fig.add_subplot(111)

        ax.bar(self.df['sec'], self.df['cal_c_sum'], width, label='water', color='#66ccff')
        ax.plot(self.df['sec'], self.df['volume'], label='air', color='#7f757f')
        ax.legend()

        canvas = FigureCanvas(fig)
        canvas.draw()

        self.horizontalLayout_4.addWidget(canvas)

        canvas.show()


app = QApplication(sys.argv)
main_dialog = MainDialog()
main_dialog.show()
app.exec_()