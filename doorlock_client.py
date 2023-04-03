import sys
import threading
import time
import urllib3.exceptions
import datetime

import matplotlib.pyplot as plt
import os
import cv2
import serial
import requests

import mail_check
import tkinter.messagebox
import socket
import numpy as np

from urllib.request import urlopen
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

HOST = '192.168.0.28'
PORT = 9900
app=0

sock = socket.socket()
sock.connect_ex((HOST,PORT))

ser = serial.Serial('COM6',115200)


class About(QLabel) :                    # About - record file 클릭
    def __init__(self,parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))  # 마우스 커서를 손가락 모양으로 변경

    def leaveEvent(self, event):
        QApplication.restoreOverrideCursor()  # 마우스 커서를 기본값으로 돌림

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            folder_path = "C:\Record_File"  # 열고자 하는 폴더 경로
            os.startfile(folder_path)  # 폴더 열기

class Menu(QLabel) :                 # 라벨 클릭 이벤트
    def __init__(self,parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))  # 마우스 커서를 손가락 모양으로 변경

    def leaveEvent(self, event):
        QApplication.restoreOverrideCursor()  # 마우스 커서를 기본값으로 돌림

class Close(QPushButton) :           # 버튼 클릭 이벤트
    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))  # 마우스 커서를 손가락 모양으로 변경

    def leaveEvent(self, event):
        QApplication.restoreOverrideCursor()  # 마우스 커서를 기본값으로 돌림

class Remote(QLabel) :
    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))

    def leaveEvent(self, event):
        QApplication.restoreOverrideCursor()

    def mousePressEvent(self, event) :
        if event.button() == Qt.LeftButton :
            ser.write("open\n".encode())
            print("원격 열림")

class MainWindow(QDialog) :

    conn_soc = None

    # 로그인 클릭 시 아이디 비번 담을 변수
    ID = None
    PW = None

    login_msg = 0
    open_msg = 0
    warning_msg = 0

    # 회원가입 - 인증번호 전송 클릭시 이름, 메일주소, 인증코드, 비밀번호 체크 담을 변수
    join_check_name = None
    join_check_email = None
    join_check_code_email = None
    join_check_confirm_password = None
    join_check_password = None

    # 회원가입 클릭시 DB에 담을 변수
    join_ID = None
    join_PW = None

    # 사운드 초기값
    sound_initial_value = 5

    # 클릭 카운트
    home_count = None
    setting_count = None
    about_count = None
    sign_up_count = None

    # 설정 - 비번변경 체크
    setting_current_password = None
    setting_change_password = None
    setting_confrim_password = None

    # 로그인 체크 ( on / off 인지 )
    login_check = None

    # DB에서 받아올 유저 데이터
    user_id = None
    user_door_lock = None
    user_safe_record = None
    user_fake_number = None
    user_random_number = None
    user_etiquette = None
    user_guest_password = None

    record_count = 0

    video_data = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()

        self.worker = Worker()
        self.worker.start()

        self.arduino = Arduino()
        self.arduino.start()

    def initUi(self):
        self.resize(1200,700)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet("background : rgb(206,233,254)")

        # 메인화면
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setYOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0,0,0,50))

        pix = QPixmap("2.png")

        # 메인프레임
        self.MainFrame = QFrame(self)
        self.MainFrame.setStyleSheet("background : white;"
                                     "border-radius : 25px")
        self.MainFrame.setGraphicsEffect(shadow)
        self.MainFrame.setGeometry(100,50,1000,600)

        # 로그인 및 회원가입 창 시 투명도 조절
        self.blur = QGraphicsBlurEffect()
        self.blur.setBlurRadius(500)

        self.trans = QLabel(self)
        self.trans.setGeometry(0,0,1200,700)
        self.trans.setStyleSheet("background : white")
        self.trans.setGraphicsEffect(self.blur)
        self.trans.setVisible(False)

        # 메인 이미지
        main_img1 = QPixmap("4.gif")
        self.main_img = QLabel(self.MainFrame)
        self.main_img.setPixmap(main_img1)
        self.main_img.setStyleSheet("background : white")
        self.main_img.setScaledContents(True)
        self.main_img.setGeometry(50,120,500,400)

        # 타이틀 제목
        self.title = QLabel(self.MainFrame)
        self.title.setText("""NO.1 SMART""")
        self.title.setStyleSheet("background : transparent;"
                                 "color : rgb(58,116,156)")
        font = QFont("Noto Sans KR",30)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setGeometry(680,270,350,200)

        # 타이틀 제목2
        self.title2 = QLabel(self.MainFrame)
        self.title2.setText("DOOR LOCK")
        self.title2.setStyleSheet("background : transparent;"
                                 "color : rgb(58,116,156)")
        font = QFont("Noto Sans KR", 30)
        font.setBold(True)
        self.title2.setFont(font)
        self.title2.setGeometry(680, 310, 350, 200)

        # 타이틀 제목3
        self.semi_title = QLabel(self.MainFrame)
        self.semi_title.setText("""소중한 공간의 안전,
스마트 도어락이 책임집니다.""")
        self.semi_title.setStyleSheet("background : transparent;"
                                      "color : rgb(191,191,191)")
        font2= QFont("Noto Sans KR",13)
        font2.setBold(True)
        self.semi_title.setFont(font2)
        self.semi_title.setGeometry(680,430,250,50)

        # 로그인창
        self.login_form = QFrame(self)
        self.login_form.setStyleSheet("background : white;"
                                      "border-style : solid;"
                                      "border-width : 1px;"
                                      "border-color : rgb(58,116,156)")
        self.login_form.setGeometry(375,125,450,450)

        # LOGIN < 제목
        self.login_name = QLabel(self.login_form)
        self.login_name.setText("LOGIN")
        self.login_name.setStyleSheet("background : transparent;"
                                      "color : rgb(58,116,156);"
                                      "border-style : solid;"
                                      "border-width : 0px")
        font = QFont("Noto Sans KR", 40)
        font.setBold(True)
        self.login_name.setFont(font)
        self.login_name.setGeometry(140,50,160,70)

        # 로그인 닫기 버튼
        self.login_exit = Menu(self.login_form)
        exit_img = QPixmap("닫기.png")
        self.login_exit.setStyleSheet("background : transparent;"
                                      "border-style : solid;"
                                      "border-width : 0px")
        self.login_exit.setPixmap(exit_img)
        self.login_exit.setScaledContents(True)
        self.login_exit.setGeometry(420,10,25,20)
        self.login_exit.mousePressEvent = self.Main_Form

        # 로그인 아이디창
        font = QFont("Noto Sans KR")
        font.setBold(True)
        self.login_ID_Edit = QLineEdit(self.login_form)
        self.login_ID_Edit.setMaxLength(20)
        self.login_ID_Edit.setStyleSheet("color : rgb(148,148,148)")
        self.login_ID_Edit.setGeometry(60,150,330,30)
        self.login_ID_Edit.focusInEvent = self.clear_ID
        self.login_ID_Edit.focusOutEvent = self.create_ID

        self.login_ID_Label = QLabel(self.login_form)
        self.login_ID_Label.setText("ID")
        self.login_ID_Label.setStyleSheet("background : transparent;"
                                          "border-width : 0px;"
                                          "color : rgb(148,148,148)")
        self.login_ID_Label.setFont(font)
        self.login_ID_Label.setGeometry(70,153,60,20)

        # 로그인 패스워드창
        self.login_PW_Edit = QLineEdit(self.login_form)
        self.login_PW_Edit.setStyleSheet("color : rgb(148,148,148)")
        self.login_PW_Edit.setMaxLength(15)
        self.login_PW_Edit.setEchoMode(QLineEdit.Password)
        self.login_PW_Edit.setGeometry(60,200,330,30)
        self.login_PW_Edit.focusInEvent = self.clear_PW
        self.login_PW_Edit.focusOutEvent = self.create_PW

        self.login_PW_Label = QLabel(self.login_form)
        self.login_PW_Label.setText("PW")
        self.login_PW_Label.setStyleSheet("background : transparent;"
                                          "border-width : 0px;"
                                          "color : rgb(148,148,148)")
        self.login_PW_Label.setFont(font)
        self.login_PW_Label.setGeometry(70,203,80,20)

        # 로그인 클릭창
        self.login_click_btn = Close(self.login_form)
        self.login_click_btn.setText("LOGIN")
        self.login_click_btn.setStyleSheet("background : rgb(58,116,156);"
                                           "color : white")
        font = QFont("Noto Sans KR", 11)
        font.setBold(True)
        self.login_click_btn.setFont(font)
        self.login_click_btn.setGeometry(60,250,330,30)
        self.login_click_btn.clicked.connect(self.login_click)

        # 아이디 비밀번호 찾기
        self.bar = QLabel(self.login_form)
        self.bar.setText("|")
        self.bar.setStyleSheet("background : transparent;"
                               "border-style : solid;"
                               "border-width : 0px;"
                               "color : rgb(148,148,148)")
        self.bar.setFont(font)
        self.bar.setGeometry(245,289,50,20)

        self.bar2 = QLabel(self.login_form)
        self.bar2.setText("|")
        self.bar2.setStyleSheet("background : transparent;"
                               "border-style : solid;"
                               "border-width : 0px;"
                               "color : rgb(148,148,148)")
        self.bar2.setFont(font)
        self.bar2.setGeometry(335, 289, 50, 20)

        self.find_id = QLabel(self.login_form)
        self.find_id.setText("아이디찾기")
        self.find_id.setStyleSheet("background : transparent;"
                                   "border-style : solid;"
                                   "border-width : 0px;"
                                   "color : rgb(148,148,148)")
        font = QFont("Noto Sans KR")
        font.setBold(True)
        self.find_id.setFont(font)
        self.find_id.setAlignment(Qt.AlignCenter)
        self.find_id.setGeometry(170,290,80,20)

        self.find_pw = QLabel(self.login_form)
        self.find_pw.setText("비밀번호찾기")
        self.find_pw.setStyleSheet("background : transparent;"
                                   "border-style : solid;"
                                   "border-width : 0px;"
                                   "color : rgb(148,148,148)")
        self.find_pw.setFont(font)
        self.find_pw.setAlignment(Qt.AlignCenter)
        self.find_pw.setGeometry(253,290,80,20)

        # 로그인 - 회원가입 라벨
        self.join_membership = Menu(self.login_form)
        self.join_membership.setText("회원가입")
        self.join_membership.setStyleSheet("background : transparent;"
                                           "border-style : solid;"
                                           "border-width : 0px;"
                                           "color : rgb(148,148,148)")
        self.join_membership.setFont(font)
        self.join_membership.setAlignment(Qt.AlignCenter)
        self.join_membership.setGeometry(330,290,80,20)
        self.join_membership.mousePressEvent = self.Join_Form

        # 로그인창 로고
        self.login_logo = QLabel(self.login_form)
        self.login_logo.setPixmap(pix)
        self.login_logo.setScaledContents(True)
        self.login_logo.setStyleSheet("background : transparent;"
                                      "border-width : 0px")
        self.login_logo.setGeometry(15,380,80,60)

        self.login_form.setVisible(False)

        # 회원가입 화면
        self.join_form = QFrame(self)
        self.join_form.setStyleSheet("background : white;"
                                      "border-style : solid;"
                                      "border-width : 1px;"
                                      "border-color : rgb(58,116,156)")
        self.join_form.setGeometry(400,60,400,580)
        self.join_form.setVisible(False)

        # 회원가입 나가기
        self.join_exit = Menu(self.join_form)
        self.join_exit.setStyleSheet("border-width : 0px")
        self.join_exit.setPixmap(exit_img)
        self.join_exit.setScaledContents(True)
        self.join_exit.setGeometry(370,10,25,20)
        self.join_exit.mousePressEvent = self.Join_Exit

        # 회원가입 < 텍스트
        font = QFont("Noto Sans KR",18)
        font.setBold(True)
        self.join_text = QLabel(self.join_form)
        self.join_text.setText("회원가입")
        self.join_text.setFont(font)
        self.join_text.setStyleSheet("border-width : 0px;"
                                     "color : rgb(148,148,148)")
        self.join_text.setGeometry(145,35,135,50)

        # 회원가입 이름 작성칸
        self.join_name_Edit = QLineEdit(self.join_form)
        self.join_name_Edit.setStyleSheet("color : rgb(148,148,148);"
                                          "border-width : 0px")
        self.join_name_Edit.setGeometry(35,117,330,30)
        self.join_name_Edit.focusInEvent = self.Join_Name_IN
        self.join_name_Edit.focusOutEvent = self.Join_Name_OUT

        self.join_name_Edit_under_bar = QLabel(self.join_form)
        self.join_name_Edit_under_bar.setStyleSheet("border-color : rgb(127,127,127)")
        self.join_name_Edit_under_bar.setGeometry(35,147,330,1)

        # 회원가입 이름 텍스트
        font = QFont("Noto Sans KR",10)
        font.setBold(True)
        self.join_name = QLabel(self.join_form)
        self.join_name.setText("이름")
        self.join_name.setFont(font)
        self.join_name.setStyleSheet("border-width : 0px;"
                                     "color : rgb(148,148,148)")
        self.join_name.setGeometry(35,95,100,20)

        # 회원가입 이름 설명 라벨
        semi_font = QFont("Noto Sans KR",8)
        #semi_font.setBold(True)
        self.join_name_label = QLabel(self.join_form)
        self.join_name_label.setText("실명을 입력하세요")
        self.join_name_label.setStyleSheet("border-width : 0px;"
                                           "color : rgb(180,180,180)")
        self.join_name_label.setFont(semi_font)
        self.join_name_label.setGeometry(35,122,100,20)

        # 회원가입 이메일 작성칸
        self.join_E_mail_Edit = QLineEdit(self.join_form)
        self.join_E_mail_Edit.setStyleSheet("color : rgb(148,148,148);"
                                            "border-width : 0px")
        self.join_E_mail_Edit.setGeometry(35,197,245,30)
        self.join_E_mail_Edit.setMaxLength(30)
        self.join_E_mail_Edit.focusInEvent = self.Join_Email_IN
        self.join_E_mail_Edit.focusOutEvent = self.Join_Email_OUT

        self.join_E_mail_under_bar = QLabel(self.join_form)
        self.join_E_mail_under_bar.setStyleSheet("border-color : rgb(127,127,127)")
        self.join_E_mail_under_bar.setGeometry(35,227,245,1)

        # 회원가입 이메일 텍스트
        self.join_E_mail = QLabel(self.join_form)
        self.join_E_mail.setFont(font)
        self.join_E_mail.setText("아이디(이메일)")
        self.join_E_mail.setStyleSheet("border-width : 0px;"
                                       "color : rgb(148,148,148)")
        self.join_E_mail.setGeometry(35,175,100,20)

        # 회원가입 이메일 설명 라벨
        self.join_E_mail_label = QLabel(self.join_form)
        self.join_E_mail_label.setFont(semi_font)
        self.join_E_mail_label.setText("이메일 주소")
        self.join_E_mail_label.setStyleSheet("border-width : 0px;"
                                             "color : rgb(180,180,180)")
        self.join_E_mail_label.setGeometry(35,202,100,20)

        # 이메일 코드 작성칸
        self.join_code_Edit = QLineEdit(self.join_form)
        self.join_code_Edit.setStyleSheet("color : rgb(148,148,148);"
                                          "border-width : 0px")
        self.join_code_Edit.setGeometry(35,277,330,30)
        self.join_code_Edit.focusInEvent = self.Join_Email_Code_IN
        self.join_code_Edit.focusOutEvent = self.Join_Email_Code_OUT

        self.join_code_Edit_under_bar = QLabel(self.join_form)
        self.join_code_Edit_under_bar.setStyleSheet("border-color : rgb(127,127,127)")
        self.join_code_Edit_under_bar.setGeometry(35,307,330,1)

        # 회원가입 메일 인증
        self.join_code = QLabel(self.join_form)
        self.join_code.setText("이메일 인증")
        self.join_code.setFont(font)
        self.join_code.setStyleSheet("border-width : 0px;"
                                     "color : rgb(148,148,148)")
        self.join_code.setGeometry(35,255,100,20)

        # 회원가입 메일 인증 설명 라벨
        self.join_code_label = QLabel(self.join_form)
        self.join_code_label.setText("인증번호 입력")
        self.join_code_label.setFont(semi_font)
        self.join_code_label.setStyleSheet("border-width : 0px;"
                                           "color : rgb(180,180,180)")
        self.join_code_label.setGeometry(35,282,100,20)

        # 회원가입 비밀번호 작성칸
        self.join_PW_Edit = QLineEdit(self.join_form)
        self.join_PW_Edit.setStyleSheet("color : rgb(148,148,148);"
                                        "border-width : 0px")
        self.join_PW_Edit.setGeometry(35,357,330,30)
        self.join_PW_Edit.setEchoMode(QLineEdit.Password)
        self.join_PW_Edit.focusInEvent = self.Join_PassWord_IN
        self.join_PW_Edit.focusOutEvent = self.Join_PassWord_OUT

        self.join_PW_Edit_under_bar = QLabel(self.join_form)
        self.join_PW_Edit_under_bar.setStyleSheet("border-color : rgb(127,127,127)")
        self.join_PW_Edit_under_bar.setGeometry(35,387,330,1)

        # 회원가입 비밀번호 안내문구
        self.join_PW_info = QLabel(self.join_form)
        self.join_PW_info.setGeometry(35,393,330,20)
        self.join_PW_info.setVisible(False)

        # 회원가입 비밀번호 텍스트
        self.join_PW = QLabel(self.join_form)
        self.join_PW.setText("비밀번호")
        self.join_PW.setFont(font)
        self.join_PW.setStyleSheet("border-width : 0px;"
                                   "color : rgb(148,148,148)")
        self.join_PW.setGeometry(35,335,100,20)

        # 회원가입 비밀번호 텍스트 설명 라벨
        self.join_PW_label = QLabel(self.join_form)
        self.join_PW_label.setText("비밀번호")
        self.join_PW_label.setFont(semi_font)
        self.join_PW_label.setStyleSheet("border-width : 0px;"
                                         "color : rgb(180,180,180)")
        self.join_PW_label.setGeometry(35,362,100,20)

        # 회원가입 비밀번호 재확인칸
        self.join_Conf_PW_Edit = QLineEdit(self.join_form)
        self.join_Conf_PW_Edit.setStyleSheet("color : rgb(148,148,148);"
                                             "border-width : 0px")
        self.join_Conf_PW_Edit.setGeometry(35,437,330,30)
        self.join_Conf_PW_Edit.setEchoMode(QLineEdit.Password)
        self.join_Conf_PW_Edit.focusInEvent = self.Join_PassWord_Confirm_IN
        self.join_Conf_PW_Edit.focusOutEvent = self.Join_PassWord_Confirm_OUT

        self.join_Conf_PW_Edit_under_bar = QLabel(self.join_form)
        self.join_Conf_PW_Edit_under_bar.setStyleSheet("border-color : rgb(127,127,127)")
        self.join_Conf_PW_Edit_under_bar.setGeometry(35,467,330,1)

        # 회원가입 비밀번호 재확인 체크 이미지
        self.join_Conf_PW_img = QLabel(self.join_form)
        self.join_Conf_PW_img.setStyleSheet("border-width : 0px;")
        self.join_Conf_PW_img.setGeometry(335,437,25,25)
        self.join_Conf_PW_img.setVisible(False)

        # 회원가입 비밀번호 재확인 텍스트
        self.join_Conf_PW = QLabel(self.join_form)
        self.join_Conf_PW.setFont(font)
        self.join_Conf_PW.setText("비밀번호 확인")
        self.join_Conf_PW.setStyleSheet("border-width : 0px;"
                                        "color : rgb(148,148,148)")
        self.join_Conf_PW.setGeometry(35,415,110,20)

        # 회원가입 비밀번호 재확인 설명 라벨
        self.join_Conf_PW_label = QLabel(self.join_form)
        self.join_Conf_PW_label.setText("비밀번호 확인")
        self.join_Conf_PW_label.setFont(semi_font)
        self.join_Conf_PW_label.setStyleSheet("border-width : 0px;"
                                              "color : rgb(180,180,180)")
        self.join_Conf_PW_label.setGeometry(35,442,100,20)

        # 회원가입 비밀번호가 서로 일치하지 않음 설명
        self.join_Conf_PW_info = QLabel(self.join_form)
        self.join_Conf_PW_info.setGeometry(35,473,330,20)
        self.join_Conf_PW_info.setVisible(False)

        # 메일인증 클릭 버튼
        mail_font = QFont("Noto Sans KR",9)
        mail_font.setBold(True)
        self.join_E_mail_check = Close(self.join_form)
        self.join_E_mail_check.setText("인증번호 전송")
        self.join_E_mail_check.setFont(mail_font)
        self.join_E_mail_check.setStyleSheet("border-width : 1px;"
                                             "border-style : solid;"
                                             "border-radius : 15px;"
                                             "color : rgb(58,116,156)")
        self.join_E_mail_check.setGeometry(280,197,90,30)
        self.join_E_mail_check.clicked.connect(self.Join_Send_Email)

        # 회원가입 버튼
        join_title_font = QFont("Noto Sans KR",13)
        join_title_font.setBold(True)

        self.join_click = Close(self.join_form)
        self.join_click.setText("가입하기")
        self.join_click.setFont(join_title_font)
        self.join_click.setStyleSheet("border-width : 1px;"
                                      "border-style : solid;"
                                      "border-radius : 20px;"
                                      "color : white;"
                                      "background : rgb(58,116,156)")
        self.join_click.setGeometry(35,500,330,40)
        self.join_click.clicked.connect(self.Join_Create_Account)

        # 설정화면 프레임
        setting_shadow = QGraphicsDropShadowEffect()
        setting_shadow.setBlurRadius(50)
        setting_shadow.setYOffset(0)
        setting_shadow.setYOffset(0)
        setting_shadow.setColor(QColor(0,0,0,50))

        self.setting_frame = QFrame(self)
        self.setting_frame.setStyleSheet("background : white;"
                                         "border-radius : 25px")
        self.setting_frame.setGraphicsEffect(setting_shadow)
        self.setting_frame.setGeometry(100,50,1000,600)
        self.setting_frame.setVisible(False)

        # 설정화면 도어락 이미지
        doorlock_img = QPixmap("도어락.png")
        self.doorlockimg = QLabel(self.setting_frame)
        self.doorlockimg.setPixmap(doorlock_img)
        self.doorlockimg.setScaledContents(True)
        self.doorlockimg.setGeometry(-70,150,500,400)

        # 설정화면 도어락 표시
        circle_on = QPixmap("원형.png")
        self.circle_img = QLabel(self.setting_frame)
        self.circle_img.setPixmap(circle_on)
        self.circle_img.setScaledContents(True)
        self.circle_img.setGeometry(30,130,15,15)

        # 설정화면 도어락 이름
        doorlock_name_font = QFont("Noto Sans KR",13)
        doorlock_name_font.setBold(True)
        self.doorlock_user = QLabel(self.setting_frame)
        self.doorlock_user.setText("MY DOOR LOCK")
        self.doorlock_user.setFont(doorlock_name_font)
        self.doorlock_user.setStyleSheet("color : black")
        self.doorlock_user.setGeometry(53,126,250,20)

        # 설정화면 - 에티켓모드
        menu_font = QFont("Noto Sans KR",8)
        menu_font.setBold(True)

        iphone_img = QPixmap("아이폰.png")
        # 에티켓 배경
        menu_img = QPixmap("메뉴바.png")
        self.setting_etiquette = QLabel(self.setting_frame)
        self.setting_etiquette.setPixmap(menu_img)
        self.setting_etiquette.setScaledContents(True)
        self.setting_etiquette.setStyleSheet("border-width : 0px")
        self.setting_etiquette.setGeometry(330,400,130,130)
        # 에티켓 이미지
        etiquette_img = QPixmap("에티켓.png")
        self.etiquette_img = QLabel(self.setting_etiquette)
        self.etiquette_img.setPixmap(etiquette_img)
        self.etiquette_img.setScaledContents(True)
        self.etiquette_img.setGeometry(20,45,45,45)
        # 에티켓 텍스트
        self.setting_etiquette_text = QLabel(self.setting_etiquette)
        self.setting_etiquette_text.setText("Etiquette")
        self.setting_etiquette_text.setFont(menu_font)
        self.setting_etiquette_text.setStyleSheet("color : rgb(83,83,83)")
        self.setting_etiquette_text.setGeometry(20,95,80,20)
        # 에티켓 버튼1
        self.etiquette_btn = QLabel(self.setting_etiquette)
        self.etiquette_btn.setStyleSheet("background : rgb(217,217,217);"
                                         "border-radius : 10px")
        self.etiquette_btn.setGeometry(65,20,50,20)
        # 에티켓 버튼2
        self.etiquette_btn1 =Menu(self.setting_etiquette)
        self.etiquette_btn1.setPixmap(iphone_img)
        self.etiquette_btn1.setScaledContents(True)
        self.etiquette_btn1.setStyleSheet("background : transparent")
        self.etiquette_btn1.setGeometry(68,20,20,20)
        self.etiquette_btn1.mousePressEvent = self.Setting_User_Etiqutte

        # 설정화면 - 안전녹화
        self.safe_record = QLabel(self.setting_frame)
        self.safe_record.setPixmap(menu_img)
        self.safe_record.setScaledContents(True)
        self.safe_record.setGeometry(490,400,130,130)
        # 안전녹화 이미지
        record_img = QPixmap("녹화.png")
        self.record_img = QLabel(self.safe_record)
        self.record_img.setPixmap(record_img)
        self.record_img.setScaledContents(True)
        self.record_img.setGeometry(20,45,45,45)
        # 안전녹화 텍스트
        self.safe_record_text = QLabel(self.safe_record)
        self.safe_record_text.setText("Safe record")
        self.safe_record_text.setFont(menu_font)
        self.safe_record_text.setStyleSheet("color : rgb(83,83,83)")
        self.safe_record_text.setGeometry(20,95,80,20)
        # 안전녹화 버튼1
        self.safe_record_btn = QLabel(self.safe_record)
        self.safe_record_btn.setStyleSheet("background : rgb(217,217,217);"
                                           "border-radius : 10px")
        self.safe_record_btn.setGeometry(65,20,50,20)
        # 안전녹화 버튼2
        self.safe_record_btn1 =Menu(self.safe_record)
        self.safe_record_btn1.setPixmap(iphone_img)
        self.safe_record_btn1.setScaledContents(True)
        self.safe_record_btn1.setStyleSheet("background : transparent")
        self.safe_record_btn1.setGeometry(68,20,20,20)
        self.safe_record_btn1.mousePressEvent = self.Setting_User_Safe_Record

        # 설정화면 - 허수기능
        self.fake_function = QLabel(self.setting_frame)
        self.fake_function.setPixmap(menu_img)
        self.fake_function.setScaledContents(True)
        self.fake_function.setGeometry(650,400,130,130)
        # 허수기능 이미지
        fake_img = QPixmap("허수.png")
        self.fake_img = QLabel(self.fake_function)
        self.fake_img.setPixmap(fake_img)
        self.fake_img.setScaledContents(True)
        self.fake_img.setGeometry(20,45,45,45)
        # 허수기능 텍스트
        self.fake_function_text = QLabel(self.fake_function)
        self.fake_function_text.setText("Fake Number")
        self.fake_function_text.setFont(menu_font)
        self.fake_function_text.setStyleSheet("color : rgb(83,83,83)")
        self.fake_function_text.setGeometry(20,95,80,20)
        # 허수기능 버튼1
        self.fake_function_btn = QLabel(self.fake_function)
        self.fake_function_btn.setStyleSheet("background : rgb(217,217,217);"
                                             "border-radius : 10px")
        self.fake_function_btn.setGeometry(65,20,50,20)
        # 허수기능 버튼2
        self.fake_function_btn1 = Menu(self.fake_function)
        self.fake_function_btn1.setPixmap(iphone_img)
        self.fake_function_btn1.setScaledContents(True)
        self.fake_function_btn1.setStyleSheet("background : transparent")
        self.fake_function_btn1.setGeometry(68,20,20,20)
        self.fake_function_btn1.mousePressEvent = self.Setting_User_Fake_Num

        # 설정화면 - 랜덤숫자
        self.random_function = QLabel(self.setting_frame)
        self.random_function.setPixmap(menu_img)
        self.random_function.setScaledContents(True)
        self.random_function.setGeometry(810,400,130,130)
        # 랜덤숫자 이미지
        random_img = QPixmap("랜덤숫자.png")
        self.random_img = QLabel(self.random_function)
        self.random_img.setPixmap(random_img)
        self.random_img.setScaledContents(True)
        self.random_img.setGeometry(20,45,45,45)
        # 랜덤숫자 텍스트
        self.random_function_text = QLabel(self.random_function)
        self.random_function_text.setText("Random Number")
        self.random_function_text.setStyleSheet("color : rgb(83,83,83)")
        self.random_function_text.setFont(menu_font)
        self.random_function_text.setGeometry(20,95,100,20)
        # 랜덤숫자 버튼1
        self.random_function_btn = QLabel(self.random_function)
        self.random_function_btn.setStyleSheet("background : rgb(217,217,217);"
                                               "border-radius : 10px")
        self.random_function_btn.setGeometry(65,20,50,20)
        # 랜덤숫자 버튼2
        self.random_function_btn1 = Menu(self.random_function)
        self.random_function_btn1.setPixmap(iphone_img)
        self.random_function_btn1.setScaledContents(True)
        self.random_function_btn1.setStyleSheet("background : transparent")
        self.random_function_btn1.setGeometry(68,20,20,20)
        self.random_function_btn1.mousePressEvent = self.Setting_User_Random_Num

        # 설정화면 - 비번변경
        pw_so_font = QFont("Noto Sans KR",10)
        pw_so_font.setBold(True)

        setting_pw_font = QFont("Noto Sans KR",10)
        setting_pw_font.setBold(True)

        long_menu = QPixmap("긴메뉴바.png")
        self.doorlock_change_password = QLabel(self.setting_frame)
        self.doorlock_change_password.setPixmap(long_menu)
        self.doorlock_change_password.setScaledContents(True)
        self.doorlock_change_password.setGeometry(330,150,300,235)
        # 비번 변경 텍스트
        self.doorlock_change_password_text = QLabel(self.doorlock_change_password)
        self.doorlock_change_password_text.setText("Change Password")
        self.doorlock_change_password_text.setFont(pw_so_font)
        self.doorlock_change_password_text.setStyleSheet("color : rgb(83,83,83)")
        self.doorlock_change_password_text.setGeometry(90,17,150,22)
        # 비번 현재변경 작성칸
        self.doorlock_change_password_current_edit = QLineEdit(self.doorlock_change_password)
        self.doorlock_change_password_current_edit.setText("   current password")
        self.doorlock_change_password_current_edit.setFont(setting_pw_font)
        self.doorlock_change_password_current_edit.setStyleSheet("color : rgb(191,191,191);"
                                                                 "border-width : 1px;"
                                                                 "border-style : solid;"
                                                                 "border-color : rgb(83,83,83);"
                                                                 "border-radius : 15px")
        self.doorlock_change_password_current_edit.setGeometry(20,47,260,35)
        self.doorlock_change_password_current_edit.focusInEvent = self.Setting_CurrentUser_FocusIn
        self.doorlock_change_password_current_edit.focusOutEvent = self.Setting_CurrentUser_FocusOut
        # 변경할 비번 작성칸
        self.doorlock_change_password_new_edit = QLineEdit(self.doorlock_change_password)
        self.doorlock_change_password_new_edit.setText("   new password")
        self.doorlock_change_password_new_edit.setFont(setting_pw_font)
        self.doorlock_change_password_new_edit.setStyleSheet("color : rgb(191,191,191);"
                                                             "border-width : 1px;"
                                                             "border-style : solid;"
                                                             "border-color : rgb(83,83,83);"
                                                             "border-radius : 15px")
        self.doorlock_change_password_new_edit.setGeometry(20,92,260,35)
        self.doorlock_change_password_new_edit.focusInEvent = self.Setting_ChangeUser_FocusIn
        self.doorlock_change_password_new_edit.focusOutEvent = self.Setting_ChangeUser_FocusOut
        # 변경할 비번 재확인칸
        self.doorlock_change_password_confirm_edit = QLineEdit(self.doorlock_change_password)
        self.doorlock_change_password_confirm_edit.setText("   confirm password")
        self.doorlock_change_password_confirm_edit.setFont(setting_pw_font)
        self.doorlock_change_password_confirm_edit.setStyleSheet("color : rgb(191,191,191);"
                                                                 "border-width : 1px;"
                                                                 "border-style : solid;"
                                                                 "border-color : rgb(83,83,83);"
                                                                 "border-radius : 15px")
        self.doorlock_change_password_confirm_edit.setGeometry(20,137,260,35)
        self.doorlock_change_password_confirm_edit.focusInEvent = self.Setting_ConfirmUser_FocusIn
        self.doorlock_change_password_confirm_edit.focusOutEvent = self.Setting_ConfirmUser_FocusOut
        # 비밀번호 바꾸기 버튼
        self.doorlock_change_password_change_btn = Close(self.doorlock_change_password)
        self.doorlock_change_password_change_btn.setText("Change my password")
        self.doorlock_change_password_change_btn.setFont(setting_pw_font)
        self.doorlock_change_password_change_btn.setStyleSheet("background : rgb(209,236,255);"
                                                               "color : rgb(83,83,83);"
                                                               "border-wdith : 0px;"
                                                               "border-radius : 15px")
        self.doorlock_change_password_change_btn.setGeometry(20,182,260,35)
        self.doorlock_change_password_change_btn.clicked.connect(self.Setting_User_Password)

        # 설정화면 - 게스트 비번 설정
        self.guset_password = QLabel(self.setting_frame)
        self.guset_password.setPixmap(long_menu)
        self.guset_password.setScaledContents(True)
        self.guset_password.setGeometry(640,150,300,125)
        # 게스트 비번 설정 텍스트
        self.guset_password_text = QLabel(self.guset_password)
        self.guset_password_text.setText("Guest Password")
        self.guset_password_text.setFont(pw_so_font)
        self.guset_password_text.setStyleSheet("color : rgb(83,83,83)")
        self.guset_password_text.setGeometry(100,20,150,22)
        # 게스트 비번 설정 작성칸
        self.guset_password_edit = QLineEdit(self.guset_password)
        self.guset_password_edit.setText("   password")
        self.guset_password_edit.setFont(setting_pw_font)
        self.guset_password_edit.setStyleSheet("border-width : 1px;"
                                               "border-style : solid;"
                                               "border-color : rgb(83,83,83);"
                                               "border-radius : 15px;"
                                               "color : rgb(191,191,191)")
        self.guset_password_edit.setGeometry(20,50,260,35)
        self.guset_password_edit.focusInEvent = self.Setting_Guest_FocusIn
        self.guset_password_edit.focusOutEvent = self.Setting_Guest_FocusOut
        # 게스트 비번 설정 저장 버튼
        self.guset_password_ok_btn = Close(self.guset_password)
        self.guset_password_ok_btn.setText("OK")
        self.guset_password_ok_btn.setFont(setting_pw_font)
        self.guset_password_ok_btn.setStyleSheet("border-style : solid;"
                                                 "border-radius : 10px;"
                                                 "background : rgb(209,236,255);"
                                                 "color : rgb(83,83,83)")
        self.guset_password_ok_btn.setGeometry(20,90,125,20)
        self.guset_password_ok_btn.clicked.connect(self.Setting_Guest_OK)
        # 게스트 비번 설정 취소 버튼
        self.guset_password_cancel_btn = Close(self.guset_password)
        self.guset_password_cancel_btn.setText("Cancel")
        self.guset_password_cancel_btn.setFont(setting_pw_font)
        self.guset_password_cancel_btn.setStyleSheet("background : rgb(209,236,255);"
                                                     "border-style : solid;"
                                                     "border-radius : 10px;"
                                                     "color : rgb(83,83,83)")
        self.guset_password_cancel_btn.setGeometry(155,90,125,20)
        self.guset_password_cancel_btn.clicked.connect(self.Setting_Guest_Cancel)

        # 설정화면 - 음량 조절
        self.sound_change = QLabel(self.setting_frame)
        self.sound_change.setPixmap(long_menu)
        self.sound_change.setScaledContents(True)
        self.sound_change.setGeometry(640,285,300,95)
        # 음량조절 텍스트
        self.sound_change_text = QLabel(self.sound_change)
        self.sound_change_text.setText("Sound")
        self.sound_change_text.setFont(pw_so_font)
        self.sound_change_text.setGeometry(20,20,100,22)
        # 음량조절 슬라이더바
        self.sound_slider = QSlider(Qt.Horizontal, self.sound_change)
        self.sound_slider.setRange(1,5)
        self.sound_slider.setSingleStep(1)
        self.sound_slider.setGeometry(50,55,210,20)
        self.sound_slider.setValue(self.sound_initial_value)
        self.sound_slider.valueChanged[int].connect(self.Setting_Sound_Change)
        # 음량조절 텍스트
        sound_font = QFont("Noto Sans KR",11)
        sound_font.setBold(True)
        self.sound_slider_text = QLabel(str(self.sound_initial_value),self.sound_change)
        self.sound_slider_text.setFont(sound_font)
        self.sound_slider_text.move(275,50)
        # 음량조절 이미지
        self.sound_img = QPixmap("음량.png")
        self.nosound_img = QPixmap("음소거.png")
        self.sound_slider_img = QLabel(self.sound_change)
        self.sound_slider_img.setPixmap(self.sound_img)
        self.sound_slider_img.setScaledContents(True)
        self.sound_slider_img.setGeometry(20,53,20,20)

        # 대시보드 프레임
        dashbord_shadow = QGraphicsDropShadowEffect()
        dashbord_shadow.setBlurRadius(50)
        dashbord_shadow.setYOffset(0)
        dashbord_shadow.setYOffset(0)
        dashbord_shadow.setColor(QColor(0,0,0,50))

        self.dash_bord_frame = QFrame(self)
        self.dash_bord_frame.setStyleSheet("background : white;"
                                           "border-radius : 25px")
        self.dash_bord_frame.setGraphicsEffect(dashbord_shadow)
        self.dash_bord_frame.setGeometry(100,50,1000,600)
        self.dash_bord_frame.setVisible(False)

        # 대시보드 판
        dash_back_img = QPixmap("대시보드2.PNG")
        dash_font = QFont("Noto Sans KR",11)
        dash_font.setBold(True)

        record = QPixmap("영상.PNG")

        # 대시보드 영상판
        self.dash_bord_back1 = QLabel(self.dash_bord_frame)
        self.dash_bord_back1.setPixmap(dash_back_img)
        self.dash_bord_back1.setScaledContents(True)
        self.dash_bord_back1.setGeometry(530,100,420,450)

        self.live_cam = QLabel(self.dash_bord_back1)
        self.live_cam.setStyleSheet("border-radius : 0px")
        self.live_cam.setGeometry(10,30,400,410)

        self.live_cam_text = QLabel(self.dash_bord_back1)
        self.live_cam_text.setText("Live")
        self.live_cam_text.setStyleSheet("background : transparent;"
                                         "color : rgb(76,76,76)")
        self.live_cam_text.setFont(dash_font)
        self.live_cam_text.setGeometry(10,2,100,25)

        # 대시보드 녹화영상판
        self.dash_bord_back2 = QLabel(self.dash_bord_frame)
        self.dash_bord_back2.setPixmap(dash_back_img)
        self.dash_bord_back2.setScaledContents(True)
        self.dash_bord_back2.setGeometry(50,100,150,150)

        self.record_back = QLabel(self.dash_bord_back2)
        self.record_back.setStyleSheet("background : white;"
                                       "border-radius : 0px")
        self.record_back.setGeometry(10,10,130,130)

        self.record_text = QLabel(self.record_back)
        self.record_text.setText("Record File")
        self.record_text.setStyleSheet("background : transparent;"
                                       "color : rgb(76,76,76)")
        self.record_text.setFont(dash_font)
        self.record_text.setAlignment(Qt.AlignCenter)
        self.record_text.setGeometry(0,80,130,25)

        self.record_label = About(self.record_back)
        self.record_label.setPixmap(record)
        self.record_label.setScaledContents(True)
        self.record_label.setGeometry(37,39,56,42)

        self.record_label2 = QLabel(self.record_back)
        self.record_label2.setGeometry(0,100,130,20)

        # 대시보드 그래프판
        self.dash_bord_back3 = QLabel(self.dash_bord_frame)
        self.dash_bord_back3.setPixmap(dash_back_img)
        self.dash_bord_back3.setScaledContents(True)
        self.dash_bord_back3.setGeometry(50,260,470,290)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        layout = QVBoxLayout(self.dash_bord_back3)
        layout.addWidget(self.canvas)

        self.ax = self.fig.add_subplot(111)

        # 대시보드 게스트판
        self.open_img = QPixmap("열림.PNG")
        self.close_img = QPixmap("잠김.PNG")

        self.dash_bord_back4 = QLabel(self.dash_bord_frame)
        self.dash_bord_back4.setPixmap(dash_back_img)
        self.dash_bord_back4.setScaledContents(True)
        self.dash_bord_back4.setGeometry(210,100,150,150)

        self.guest_back = QLabel(self.dash_bord_back4)
        self.guest_back.setStyleSheet("background : white;"
                                      "border-radius : 0px")
        self.guest_back.setGeometry(10,10,130,130)

        self.guest_text = QLabel(self.guest_back)
        self.guest_text.setText("Guset Password")
        self.guest_text.setStyleSheet("background : transparent;"
                                      "color : rgb(76,76,76)")
        self.guest_text.setFont(dash_font)
        self.guest_text.setAlignment(Qt.AlignCenter)
        self.guest_text.setGeometry(0,80,130,25)

        self.guest_label = QLabel(self.guest_back)
        self.guest_label.setGeometry(43,25,44,58)

        self.about_mini_font = QFont("Noto Sans KR",8)
        self.about_mini_font.setBold(True)

        self.guest_label2= QLabel(self.guest_back)
        self.guest_label2.setGeometry(0,100,130,20)

        # 대시보드 알람판
        self.message_img = QPixmap("원격.PNG")

        self.dash_bord_back5 = QLabel(self.dash_bord_frame)
        self.dash_bord_back5.setPixmap(dash_back_img)
        self.dash_bord_back5.setScaledContents(True)
        self.dash_bord_back5.setStyleSheet("background : transparent")
        self.dash_bord_back5.setGeometry(370,100,150,150)

        self.message_back = QLabel(self.dash_bord_back5)
        self.message_back.setStyleSheet("background : white;"
                                        "border-radius : 0px")
        self.message_back.setGeometry(10,10,130,130)

        self.message_text = QLabel(self.message_back)
        self.message_text.setText("Remote")
        self.message_text.setFont(dash_font)
        self.message_text.setStyleSheet("color : rgb(76,76,76)")
        self.message_text.setAlignment(Qt.AlignCenter)
        self.message_text.setGeometry(0,80,130,25)

        self.message_label = Remote(self.message_back)
        self.message_label.setPixmap(self.message_img)
        self.message_label.setScaledContents(True)
        self.message_label.setStyleSheet("background : transparent")
        self.message_label.setGeometry(13,5,100,100)

######################### 메뉴바 맨 끝에 남아있어야할듯 ###########################

        # 화면 종료
        self.main_exit = Close(self)
        self.main_exit.setStyleSheet("border-image : url(메인닫기.png);"
                                     "background : transparent")
        self.main_exit.setGeometry(1065, 60, 25, 20)
        self.main_exit.clicked.connect(QCoreApplication.quit)

        # 메뉴바 - 홈 버튼
        menu_font = QFont("Domine", 13)
        menu_font.setBold(True)

        self.home_title = Menu(self)
        self.home_title.setText("home")
        self.home_title.setStyleSheet("background : transparent;"
                                      "color : rgb(148,148,148)")
        self.home_title.setFont(menu_font)
        self.home_title.setGeometry(715, 80, 70, 20)
        self.home_title.mousePressEvent = self.First_Form

        # 메뉴바 - about 버튼
        self.about_title = Menu(self)
        self.about_title.setText("about")
        self.about_title.setStyleSheet("background : transparent;"
                                       "color : rgb(148,148,148)")
        self.about_title.setFont(menu_font)
        self.about_title.setGeometry(800, 80, 70, 20)
        self.about_title.mousePressEvent = self.DashBord_Form

        # 메뉴바 - 설정 화면
        self.setting_btn = Menu(self)
        self.setting_btn.setText("setting")
        self.setting_btn.setStyleSheet("background : transparent;"
                                       "color : rgb(148,148,148)")
        self.setting_btn.setFont(menu_font)
        self.setting_btn.setGeometry(885,80,70,20)
        self.setting_btn.mousePressEvent = self.Setting_Form

        # 메뉴바 - 로그인 버튼
        self.login_title = Menu(self)
        self.login_title.setText("sign up")
        self.login_title.setStyleSheet("background : transparent;"
                                       "color : rgb(148,148,148)")
        self.login_title.setFont(menu_font)
        self.login_title.setGeometry(970, 80, 70, 20)
        self.login_title.mousePressEvent = self.Login_Form

        # 로고
        self.logo = QLabel(self)
        self.logo.setPixmap(pix)
        self.logo.setStyleSheet("background : transparent")
        self.logo.setScaledContents(True)
        self.logo.setGeometry(120,70,70,50)

        # 로그아웃
        logout_img = QPixmap("로그아웃.PNG")
        self.logout = Menu(self.setting_frame)
        self.logout.setPixmap(logout_img)
        self.logout.setStyleSheet("background : transparent")
        self.logout.setScaledContents(True)
        self.logout.setGeometry(20,550,22,24)
        self.logout.mousePressEvent = self.LogOut

        log_font = QFont("Noto Sans KR",9)
        self.logout_text = QLabel(self.setting_frame)
        self.logout_text.setText("로그아웃")
        self.logout_text.setFont(log_font)
        self.logout_text.setStyleSheet("color : rgb(168,207,240)")
        self.logout_text.setGeometry(47,555,100,20)

        # 동적라벨 테스트
        self.message_label = QLabel(self)
        self.message_label.setStyleSheet("background : rgb(58,116,156)")
        self.message_label.setGeometry(950,900,250,120)
        self.message_label.mousePressEvent = self.message_

        self.message_label_bar = QLabel(self.message_label)
        self.message_label_bar.setStyleSheet("border-style : solid;"
                                             "border-width : 1px;"
                                             "border-color : white")
        self.message_label_bar.setGeometry(20,30,220,1)

        logo_img = QPixmap("로고2.PNG")
        self.message_logo = QLabel(self.message_label)
        self.message_logo.setPixmap(logo_img)
        self.message_logo.setScaledContents(True)
        self.message_logo.setGeometry(20,50,35,30)

        message_exit_img = QPixmap("메인닫기2.PNG")
        self.message_exit = Menu(self.message_label)
        self.message_exit.setPixmap(message_exit_img)
        self.message_exit.setScaledContents(True)
        self.message_exit.setGeometry(236,7,10,10)

        msg_font = QFont("Noto Sans KR",8)
        msg_font.setBold(True)
        self.message_text = QLabel(self.message_label)
        self.message_text.setText("SAFE OPERATION")
        self.message_text.setFont(msg_font)
        self.message_text.setStyleSheet("color : white")
        self.message_text.setGeometry(20,5,200,20)

        self.message_text2 = QLabel(self.message_label)
        self.message_text2.setStyleSheet("color : white")
        self.message_text2.setFont(msg_font)
        self.message_text2.setGeometry(65,38,190,50)

        self.cam_threading()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_up_message)
        self.timer.start(1)

        self.center()
        self.show()

    def remoteOpen(self,event):
        ser.write("open\n".encode())
        print("하이")

    def message_(self, event):
        self.message_label.setGeometry(950, 900, 250, 120)

    def move_up_message(self):
        cur = self.message_label.pos()

        if self.login_msg == 1 :
            if "@" in self.user_id :
                name = self.user_id.split("@")
                self.message_text2.setText(f"""오늘도 안전을 책임지겠습니다!
어서오세요 {name[0]}님!""")
            else :
                self.message_text2.setText(f"""오늘도 안전을 책임지겠습니다!
어서오세요 {self.user_id}님!""")

            if cur.y() <= 600 :
                self.timer.stop()
                self.login_msg = 2
                self.timer_hide = QTimer()
                self.timer_hide.singleShot(3000,self.move_down_message)
            self.message_label.move(cur.x(),cur.y()-2)

        if self.open_msg == 1 :
            self.message_text2.setText("출입문이 열렸습니다!")
            if cur.y() <= 600 :
                self.timer.stop()
                self.open_msg = 2
                self.timer_hide = QTimer()
                self.timer_hide.singleShot(3000, self.move_down_message)
            self.message_label.move(cur.x(), cur.y() - 2)

        if self.warning_msg == 1 :
            self.message_text2.setText("누군가 침입을 시도했습니다!")
            if cur.y() <= 600 :
                self.timer.stop()
                self.warning_msg = 2
                self.timer_hide = QTimer()
                self.timer_hide.singleShot(3000, self.move_down_message)
            self.message_label.move(cur.x(), cur.y() - 2)

    def move_down_message(self):
        cur = self.message_label.pos()
        if self.login_msg == 2:
            if cur.y() >= 900:
                self.timer_hide.stop()
                self.login_msg = 0
                self.timer.start(1)
            else:
                self.message_label.move(cur.x(), cur.y() + 2)
                QTimer.singleShot(10, self.move_down_message)

        if self.open_msg == 2 :
            if cur.y() >= 900 :
                self.timer_hide.stop()
                self.open_msg = 0
                self.timer.start(1)
            else:
                self.message_label.move(cur.x(), cur.y() + 2)
                QTimer.singleShot(10, self.move_down_message)

        if self.warning_msg == 2 :
            if cur.y() >= 900 :
                self.timer_hide.stop()
                self.warning_msg = 0
                self.timer.start(1)
            else :
                self.message_label.move(cur.x(), cur.y() + 2)
                QTimer.singleShot(10, self.move_down_message)

    def update_frame(self):
        self.buffer = b''
        url = "http://192.168.4.1"  # Your url
        self.stream = urlopen(url)
        while True:
            try:
                self.buffer += self.stream.read(2560)
                head = self.buffer.find(b'\xff\xd8')
                end = self.buffer.find(b'\xff\xd9')

                if head > -1 and end > -1:
                    jpg = self.buffer[head:end + 2]
                    self.buffer = self.buffer[end + 2:]
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    h, w, c = frame.shape
                    qImg = QImage(frame.data, w, h, w * c, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qImg)
                    self.live_cam.setPixmap(pixmap)
                    self.live_cam.setScaledContents(True)
                    self.live_cam.update()

                    self.recording_buffer.append(frame)
                    current_time = time.time()

                    if self.user_id != None and self.video_data == "R" and current_time - self.recording_start_time >= 10:
                        self.save_video()
                        self.recording_buffer = self.recording_buffer[-300:]  # 마지막 300프레임만 남김
                        self.recording_start_time = current_time
                        self.video_data = None
                    else :
                        continue

            except Exception as e :
                print(e)

    def cam_threading(self):

        self.recording_buffer = []
        self.recording_start_time = time.time()

        recv_data = threading.Thread(target = self.update_frame)
        recv_data.daemon = True
        recv_data.start()

    def save_video(self):
        now = datetime.datetime.now()
        filename = "C:\Record_File\\" + f"{self.user_id}" + "-" + now.strftime("%Y-%m-%d %H-%M-%S") + ".avi"

        out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
        for frame in self.recording_buffer:
            out.write(frame)
        out.release()
        ser.write("녹화종료\n".encode())

    def clear_ID(self, event):
        self.login_ID_Label.setVisible(False)
        self.login_ID_Edit.setReadOnly(False)
        if self.login_ID_Edit.text() != "" :
            self.login_ID_Edit.selectAll()

    def create_ID(self,event):
        if self.login_ID_Edit.text() == "" :
            self.login_ID_Label.setVisible(True)
        else :
            self.login_ID_Edit.deselect()
        self.login_ID_Edit.setReadOnly(True)

    def clear_PW(self, event):
        self.login_PW_Label.setVisible(False)
        if self.login_PW_Edit.text() != "" :
            self.login_PW_Edit.selectAll()
        self.login_PW_Edit.setReadOnly(False)

    def create_PW(self, event):
        if self.login_PW_Edit.text() == "" :
            self.login_PW_Label.setVisible(True)
        else :
            self.login_PW_Edit.deselect()
        self.login_PW_Edit.setReadOnly(True)

    def login_click(self, event):
        self.ID = self.login_ID_Edit.text()
        self.PW = self.login_PW_Edit.text()
        user_account = '/로그인' + '*' + self.ID + '*' + self.PW
        if self.ID == "" or self.PW == "" :
            tkinter.messagebox.showwarning("경고","올바른 정보를 입력해주세요")
        else :
            if self.login_check == "In" :
                tkinter.messagebox.showwarning("경고","이미 로그인 중입니다")
                return
            sock.send(user_account.encode())

    def LogOut(self,event):
        answer = tkinter.messagebox.askyesno("안내","정말 로그아웃하시겠습니까?")
        if answer == True :
            self.user_id = None
            self.login_check = None
            time.sleep(0.3)
            self.MainFrame.setVisible(True)
            self.setting_frame.setVisible(False)
            self.dash_bord_frame.setVisible(False)

    def Login_Form(self,event):
        self.trans.setVisible(True)
        self.login_form.setVisible(True)
        self.trans.raise_()
        self.login_form.raise_()
        self.login_name.setFocus()

    def Main_Form(self,event):
        self.trans.setVisible(False)
        self.login_form.setVisible(False)
        self.login_ID_Label.setVisible(True)
        self.login_ID_Edit.clear()
        self.login_PW_Label.setVisible(True)
        self.login_PW_Edit.clear()

    def First_Form(self,event):
        self.setting_frame.setVisible(False)
        self.MainFrame.setVisible(True)
        self.dash_bord_frame.setVisible(False)

        self.SettingForm_FocusOut()

    def Join_Form(self,event):
        self.login_form.setVisible(False)
        self.join_form.setVisible(True)
        self.join_form.raise_()
        self.login_ID_Edit.clear()
        self.login_PW_Edit.clear()

    def Join_Exit(self,event):
        self.join_form.setVisible(False)
        self.login_form.setVisible(True)
        self.join_Conf_PW_info.setVisible(False)
        self.join_PW_info.setVisible(False)
        self.join_name_Edit.clear()
        self.join_E_mail_Edit.clear()
        self.join_code_Edit.clear()
        self.join_PW_Edit.clear()
        self.join_Conf_PW_Edit.clear()
        self.join_name_label.setVisible(True)
        self.join_E_mail_label.setVisible(True)
        self.join_code_label.setVisible(True)
        self.join_PW_label.setVisible(True)
        self.join_Conf_PW_label.setVisible(True)

    def Join_Name_IN(self,event):
        self.join_name_label.setVisible(False)
        self.join_name_Edit.setReadOnly(False)

    def Join_Name_OUT(self,event):
        if self.join_name_Edit.text() == "" :
            self.join_name_label.setVisible(True)
        self.join_name_Edit.setReadOnly(True)

    def Join_Email_IN(self,event):
        self.join_E_mail_label.setVisible(False)
        self.join_E_mail_Edit.setReadOnly(False)

    def Join_Email_OUT(self,event):
        if self.join_E_mail_Edit.text() == "" :
            self.join_E_mail_label.setVisible(True)
        self.join_E_mail_Edit.setReadOnly(True)

    def Join_Email_Code_IN(self,event):
        self.join_code_label.setVisible(False)
        self.join_code_Edit.setReadOnly(False)

    def Join_Email_Code_OUT(self,event):
        if self.join_code_Edit.text() == "" :
            self.join_code_label.setVisible(True)
        self.join_code_Edit.setReadOnly(True)

    def Join_PassWord_IN(self,event):
        self.join_PW_label.setVisible(False)
        self.join_PW_Edit.setReadOnly(False)

    def Join_PassWord_OUT(self,event):
        pw_font = QFont("Noto Sans KR", 8)
        if self.join_PW_Edit.text() == "" :
            self.join_PW_label.setVisible(True)
            self.join_PW_info.setVisible(False)
        if self.join_PW_Edit.text().isalnum() or 1 <= len(self.join_PW_Edit.text()) < 8 :
            self.join_PW_info.setText("- 8글자 이상, 특수문자 한 개 이상 넣어주세요")
            self.join_PW_info.setFont(pw_font)
            self.join_PW_info.setStyleSheet("border-width : 0px;"
                                            "color : red")
            self.join_PW_info.setVisible(True)
            self.join_check_password = "규칙실패"
        elif self.join_PW_Edit.text().isalnum() == False and len(self.join_PW_Edit.text()) >= 8 :
            self.join_PW_info.setText("- 올바른 비밀번호 형식입니다")
            self.join_PW_info.setFont(pw_font)
            self.join_PW_info.setStyleSheet("border-width : 0px;"
                                            "color : rgb(89,221,111)")
            self.join_PW_info.setVisible(True)
            self.join_check_password = "규칙성공"
        self.join_PW_Edit.setReadOnly(True)

    def Join_PassWord_Confirm_IN(self,event):
        self.join_Conf_PW_label.setVisible(False)
        self.join_Conf_PW_Edit.setReadOnly(False)

    def Join_PassWord_Confirm_OUT(self,event):
        pw_font = QFont("Noto Sans KR", 8)
        if self.join_Conf_PW_Edit.text() == "" :
            self.join_Conf_PW_label.setVisible(True)
            self.join_Conf_PW_info.setVisible(False)
        if self.join_Conf_PW_Edit.text() == self.join_PW_Edit.text() and len(self.join_Conf_PW_Edit.text()) >= 2 :
            self.join_Conf_PW_info.setText("- 비밀번호가 일치합니다")
            self.join_Conf_PW_info.setFont(pw_font)
            self.join_Conf_PW_info.setStyleSheet("border-width : 0px;"
                                                 "color : rgb(89,221,111)")
            self.join_Conf_PW_info.setVisible(True)
            self.join_check_confirm_password = "일치"
        elif self.join_Conf_PW_Edit.text() != self.join_PW_Edit.text() or len(self.join_Conf_PW_Edit.text()) >= 1 :
            self.join_Conf_PW_info.setText("- 비밀번호가 일치하지 않습니다")
            self.join_Conf_PW_info.setFont(pw_font)
            self.join_Conf_PW_info.setStyleSheet("border-width : 0px;"
                                                 "color : red")
            self.join_Conf_PW_info.setVisible(True)
            self.join_check_confirm_password = "불일치"
        self.join_Conf_PW_Edit.setReadOnly(True)

    def Join_Send_Email(self,event):
        self.join_check_name = self.join_name_Edit.text()
        self.join_check_email = self.join_E_mail_Edit.text()
        if '@' not in self.join_check_email :
            tkinter.messagebox.showwarning("경고","올바른 메일정보를\n입력해주세요.")
        elif self.join_check_name == "" :
            tkinter.messagebox.showwarning("경고","올바른 이름을\n입력해주세요.")
        else :
            mail_text = "/이메일인증"+ '*' + self.join_check_name + '*' +self.join_check_email
            sock.send(mail_text.encode())

    def Join_Create_Account(self,event):
        if self.join_name_Edit.text() == "" :
            tkinter.messagebox.showinfo("안내","이름은 필수항목입니다")
            self.join_name_Edit.setFocus()

        elif self.join_E_mail_Edit.text() == "" :
            tkinter.messagebox.showinfo("안내","이메일은 필수항목입니다")
            self.join_E_mail_Edit.setFocus()

        elif self.join_code_Edit.text() == "" :
            tkinter.messagebox.showinfo("안내","인증번호를 입력해주세요")
            self.join_code_Edit.setFocus()

        elif self.join_PW_Edit.text() == "" :
            tkinter.messagebox.showinfo("안내","비밀번호를 입력해주세요")
            self.join_PW_Edit.setFocus()

        elif self.join_check_password == "규칙실패":
            tkinter.messagebox.showinfo("안내", "비밀번호 규칙이 옳바르지 않습니다")
            self.join_PW_Edit.setFocus()
            self.join_check_password = None

        elif self.join_Conf_PW_Edit.text() == "" :
            tkinter.messagebox.showinfo("안내","비밀번호를 확인해주세요")
            self.join_Conf_PW_Edit.setFocus()

        elif self.join_check_confirm_password == "불일치" :
            tkinter.messagebox.showinfo("안내","비밀번호가 일치하지 않습니다")
            self.join_Conf_PW_Edit.setFocus()
            self.join_check_confirm_password = None

        elif self.join_check_code_email != "인증번호 전송완료" :
            tkinter.messagebox.showinfo("안내","인증번호 전송 버튼을 눌러주세요")
            self.join_check_code_email = None

        else :
            new_user_info = "/회원가입" + "*" + self.join_name_Edit.text() + "*" + self.join_E_mail_Edit.text() + "*" + self.join_code_Edit.text() + "*" + self.join_PW_Edit.text()
            sock.send(new_user_info.encode())

    def Setting_Form(self,event):
        self.home_count = 0
        self.setting_count = 1
        self.about_count = 0
        self.sign_up_count = 0

        if self.user_id is None :
            tkinter.messagebox.showwarning("경고","로그인 후 이용 가능합니다")

        else :
            self.MainFrame.setVisible(False)
            self.setting_frame.setVisible(True)
            self.dash_bord_frame.setVisible(False)

            if self.ID is None :
                self.circle_img.setVisible(False)

            else :
                name = self.ID.split("@")
                self.doorlock_user.setText(f"{name[0]}님의 DOOR LOCK")
                self.circle_img.setVisible(True)

            if self.user_etiquette == '1' :
                self.etiquette_btn1.move(92,20)
                self.etiquette_btn.setStyleSheet("background : rgb(0,255,0);"
                                                 "border-radius : 10px")

            if self.user_safe_record == '1' :
                self.safe_record_btn1.move(92,20)
                self.safe_record_btn.setStyleSheet("background : rgb(0,255,0);"
                                                   "border-radius : 10px")

            if self.user_fake_number == '1' :
                self.fake_function_btn1.move(92,20)
                self.fake_function_btn.setStyleSheet("background : rgb(0,255,0);"
                                                     "border-radius : 10px")

            if self.user_random_number == '1' :
                self.random_function_btn1.move(92,20)
                self.random_function_btn.setStyleSheet("background : rgb(0,255,0);"
                                                       "border-radius : 10px")

    def Setting_Sound_Change(self,value):
        self.sound_initial_value = value
        print("사운드 :",self.sound_initial_value)
        if value == 1 :
            ser.write("sound 233.08\n".encode())

        if value == 2 :
            ser.write("sound 466.16\n".encode())

        if value == 3 :
            ser.write("sound 932.33\n".encode())

        if value == 4 :
            ser.write("sound 1864.66\n".encode())

        if value == 5 :
            ser.write("sound 3729.31\n".encode())

        self.sound_slider_img.setPixmap(self.sound_img)
        self.sound_slider_img.setScaledContents(True)
        self.sound_slider_text.setText(str(self.sound_initial_value))
        self.sound_slider_text.adjustSize()
        self.sound_slider_text.repaint()

    def Setting_Guest_FocusIn(self,event):
        only_int = QIntValidator()
        self.guset_password_edit.clear()
        self.guset_password_edit.setReadOnly(False)
        self.guset_password_edit.setValidator(only_int)
        self.guset_password_edit.setStyleSheet("color : rgb(191,191,191);"
                                               "border-style : solid;"
                                               "border-width : 1px;"
                                               "border-color : rgb(83,83,83);"
                                               "border-radius : 15px")
        self.guset_password_edit.setEchoMode(QLineEdit.Password)

    def Setting_Guest_FocusOut(self,event):
        if self.guset_password_edit.text() == "" :
            self.guset_password_edit.setText("   password")
            self.guset_password_edit.setStyleSheet("color : rgb(191,191,191);"
                                                   "border-style : solid;"
                                                   "border-width : 1px;"
                                                   "border-color : rgb(83,83,83);"
                                                   "border-radius : 15px")
            self.guset_password_edit.setEchoMode(QLineEdit.Normal)
        self.guset_password_edit.setReadOnly(True)

    def Setting_Guest_OK(self,event):
        text = self.guset_password_edit.text()

        if text == "   password" or text == "" or len(text) <= 3 :
            return tkinter.messagebox.showwarning("경고","비밀번호를 제대로 설정해주세요")

        if self.user_guest_password == None :
            send_data = '/guest_pw'+"*"+self.user_id+"*"+text
            sock.send(send_data.encode())

        elif self.user_guest_password != None :
            if self.user_guest_password == text :
                tkinter.messagebox.showinfo("경고","이미 사용중인 비밀번호입니다")
            else :
                send_data = '/guest_pw' + "*" + self.user_id + "*" + text
                sock.send(send_data.encode())

    def Setting_Guest_Cancel(self,event):
        response = tkinter.messagebox.askyesno("안내","정말 취소하시겠습니까?")
        if response == True :
            self.guset_password_edit.clear()
            self.guset_password_edit.setText("   password")
            self.guset_password_edit.setStyleSheet("color : rgb(191,191,191);"
                                                   "border-style : solid;"
                                                   "border-width : 1px;"
                                                   "border-color : rgb(83,83,83);"
                                                   "border-radius : 15px")
            self.guset_password_edit.setEchoMode(QLineEdit.Normal)

    def Setting_CurrentUser_FocusIn(self,event):
        only_int = QIntValidator()
        self.doorlock_change_password_current_edit.clear()
        self.doorlock_change_password_current_edit.setValidator(only_int)
        self.doorlock_change_password_current_edit.setReadOnly(False)
        self.doorlock_change_password_current_edit.setStyleSheet("color : rgb(191,191,191);"
                                                                 "border-style : solid;"
                                                                 "border-width : 1px;"
                                                                 "border-radius : 15px;"
                                                                 "border-color : rgb(83,83,83)")
        self.doorlock_change_password_current_edit.setEchoMode(QLineEdit.Password)

    def Setting_CurrentUser_FocusOut(self,event):
        if self.doorlock_change_password_current_edit.text() == "" :
            self.doorlock_change_password_current_edit.setText("   current password")
            self.doorlock_change_password_current_edit.setEchoMode(QLineEdit.Normal)
        self.doorlock_change_password_current_edit.setReadOnly(True)

    def Setting_ChangeUser_FocusIn(self,event):
        only_int = QIntValidator()
        self.doorlock_change_password_new_edit.clear()
        self.doorlock_change_password_new_edit.setValidator(only_int)
        self.doorlock_change_password_new_edit.setReadOnly(False)
        self.doorlock_change_password_new_edit.setStyleSheet("color : rgb(191,191,191);"
                                                             "border-style : solid;"
                                                             "border-width : 1px;"
                                                             "border-radius : 15px;"
                                                             "border-color : rgb(83,83,83)")
        self.doorlock_change_password_new_edit.setEchoMode(QLineEdit.Password)

    def Setting_ChangeUser_FocusOut(self,event):
        if self.doorlock_change_password_new_edit.text() == "" :
            self.doorlock_change_password_new_edit.setText("   new password")
            self.doorlock_change_password_new_edit.setEchoMode(QLineEdit.Normal)
        self.doorlock_change_password_new_edit.setReadOnly(True)

    def Setting_ConfirmUser_FocusIn(self,event):
        only_int = QIntValidator()
        self.doorlock_change_password_confirm_edit.setValidator(only_int)
        self.doorlock_change_password_confirm_edit.clear()
        self.doorlock_change_password_confirm_edit.setReadOnly(False)
        self.doorlock_change_password_confirm_edit.setStyleSheet("color : rgb(191,191,191);"
                                                                 "border-style : solid;"
                                                                 "border-width : 1px;"
                                                                 "border-radius : 15px;"
                                                                 "border-color : rgb(83,83,83)")
        self.doorlock_change_password_confirm_edit.setEchoMode(QLineEdit.Password)

    def Setting_ConfirmUser_FocusOut(self,event):
        if self.doorlock_change_password_confirm_edit.text() == "" :
            self.doorlock_change_password_confirm_edit.setText("   confirm password")
            self.doorlock_change_password_confirm_edit.setEchoMode(QLineEdit.Normal)
        self.doorlock_change_password_confirm_edit.setReadOnly(True)

    def Setting_User_Password(self,event):
        self.setting_change_password = self.doorlock_change_password_new_edit.text()
        self.setting_confrim_password = self.doorlock_change_password_confirm_edit.text()
        if self.user_door_lock == self.doorlock_change_password_current_edit.text() :
            if self.setting_change_password == self.setting_confrim_password :
                if self.doorlock_change_password_current_edit.text() == self.setting_change_password :
                    return tkinter.messagebox.showwarning("경고","현재와 동일한 비밀번호입니다")
                if self.user_id != None :
                    password_change_data = '/door_pw' + "*" + self.user_id + "*" + self.setting_change_password
                    sock.send(password_change_data.encode())
            else :
                tkinter.messagebox.showwarning("경고","변경할 비밀번호가 일치하지 않습니다")
        else :
            tkinter.messagebox.showwarning("경고","현재 비밀번호가 일치하지 않습니다")

    def Setting_User_Etiqutte(self,event):
        if self.user_etiquette == '0' :
            self.etiquette_btn1.move(92,20)
            self.etiquette_btn.setStyleSheet("background : rgb(0,255,0);"
                                             "border-radius : 10px")
            self.user_etiquette = '1'
            etiquette_data = "/etiquette" + "*" + self.user_id + '*' + self.user_etiquette
            sock.send(etiquette_data.encode())

        elif self.user_etiquette == '1' :
            self.etiquette_btn1.move(68,20)
            self.etiquette_btn.setStyleSheet("background : rgb(217,217,217);"
                                             "border-radius : 10px")
            self.user_etiquette = '0'
            etiquette_data = "/etiquette" + "*" + self.user_id + '*' + self.user_etiquette
            sock.send(etiquette_data.encode())

    def Setting_User_Safe_Record(self,event):
        if self.user_safe_record == '0' :
            self.safe_record_btn1.move(92,20)
            self.safe_record_btn.setStyleSheet("background : rgb(0,255,0);"
                                               "border-radius : 10px")
            self.user_safe_record = '1'
            safe_data = "/safe_record" + "*" + self.user_id + '*' + self.user_safe_record
            sock.send(safe_data.encode())

        elif self.user_safe_record == "1" :
            self.safe_record_btn1.move(68,20)
            self.safe_record_btn.setStyleSheet("background : rgb(217,217,217);"
                                               "border-radius : 10px")
            self.user_safe_record = '0'
            safe_data = "/safe_record" + "*" + self.user_id + '*' + self.user_safe_record
            sock.send(safe_data.encode())

    def Setting_User_Fake_Num(self,event):
        if self.user_fake_number == '0' :
            self.fake_function_btn1.move(92,20)
            self.fake_function_btn.setStyleSheet("background : rgb(0,255,0);"
                                                 "border-radius : 10px")
            self.user_fake_number = '1'
            fake_data = "/fake_num" + "*" + self.user_id + '*' + self.user_fake_number
            sock.send(fake_data.encode())

        elif self.user_fake_number == "1" :
            self.fake_function_btn1.move(68,20)
            self.fake_function_btn.setStyleSheet("background : rgb(217,217,217);"
                                                 "border-radius : 10px")
            self.user_fake_number = '0'
            fake_data = "/fake_num" + "*" + self.user_id + '*' + self.user_fake_number
            sock.send(fake_data.encode())

    def Setting_User_Random_Num(self,event):
        if self.user_random_number == '0' :
            self.random_function_btn1.move(92,20)
            self.random_function_btn.setStyleSheet("background : rgb(0,255,0);"
                                                   "border-radius : 10px")
            self.user_random_number = '1'
            random_data = "/random_num" + "*" + self.user_id + '*' + self.user_random_number
            sock.send(random_data.encode())

        elif self.user_random_number == '1' :
            self.random_function_btn1.move(68,20)
            self.random_function_btn.setStyleSheet("background : rgb(217,217,217);"
                                                   "border-radius : 10px")
            self.user_random_number = '0'
            random_data = "/random_num" + "*" + self.user_id + '*' + self.user_random_number
            sock.send(random_data.encode())

    def SettingForm_FocusOut(self):
        self.doorlock_change_password_current_edit.setText("   current password")
        self.doorlock_change_password_current_edit.setEchoMode(QLineEdit.Normal)
        self.doorlock_change_password_current_edit.setReadOnly(True)

        self.doorlock_change_password_new_edit.setText("   new password")
        self.doorlock_change_password_new_edit.setEchoMode(QLineEdit.Normal)
        self.doorlock_change_password_new_edit.setReadOnly(True)

        self.doorlock_change_password_confirm_edit.setText("   confirm password")
        self.doorlock_change_password_confirm_edit.setEchoMode(QLineEdit.Normal)
        self.doorlock_change_password_confirm_edit.setReadOnly(True)

        self.guset_password_edit.setText("   password")
        self.guset_password_edit.setStyleSheet("color : rgb(191,191,191);"
                                               "border-style : solid;"
                                               "border-width : 1px;"
                                               "border-color : rgb(83,83,83);"
                                               "border-radius : 15px")
        self.guset_password_edit.setEchoMode(QLineEdit.Normal)
        self.guset_password_edit.setReadOnly(True)

    def DashBord_Form(self,event):

        self.SettingForm_FocusOut()

        if self.user_id == None :
            tkinter.messagebox.showwarning("경고","로그인 후 이용 가능합니다")

        else :
            send_data = "/Graph Data" + "*" + self.user_id
            sock.send(send_data.encode())

            self.MainFrame.setVisible(False)
            self.setting_frame.setVisible(False)
            self.dash_bord_frame.setVisible(True)

            if self.user_guest_password == None :
                self.guest_label.setPixmap(self.open_img)
                self.guest_label.setScaledContents(True)
                self.guest_label.setStyleSheet("background : transparent")

                self.guest_label2.setText("not set")
                self.guest_label2.setFont(self.about_mini_font)
                self.guest_label2.setAlignment(Qt.AlignCenter)

            if self.user_guest_password != None :
                self.guest_label.setPixmap(self.close_img)
                self.guest_label.setScaledContents(True)
                self.guest_label.setStyleSheet("background : transparent")

                self.guest_label2.setText("exists")
                self.guest_label2.setFont(self.about_mini_font)
                self.guest_label2.setAlignment(Qt.AlignCenter)

            folder_path = "C:\Record_File"

            if os.path.exists(folder_path) :
                for i in os.listdir(folder_path) :
                    if self.user_id in i :
                        if os.path.isfile(os.path.join(folder_path, i)) :
                            self.record_count += 1
            else :
                os.makedirs(folder_path)
            self.record_label2.setText(f"file : {self.record_count}")
            self.record_label2.setFont(self.about_mini_font)
            self.record_label2.setAlignment(Qt.AlignCenter)

            self.record_count = 0

    def center(self):
        frame = self.frameGeometry()
        center_frame = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center_frame)
        self.move(frame.topLeft())

class Worker(QThread) :
    def run(self):
        global msg_call, sock
        while True :
            msg = sock.recv(1024)
            msg_call = msg.decode('utf-8')
            print("받아오는 메시지 :",msg_call)

            if "/Graph" in msg_call :
                d = 0
                access = []
                warning = []
                recv_data = msg_call.split("*")
                for i in recv_data :
                    if i.isdigit() == True :
                        d += 1
                        if d >= 8 :
                            warning.append(int(i))
                        else :
                            access.append(int(i))

                x = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

                show.ax.clear()
                show.ax.plot(x,access,label="Access Status",color='#cee9fe',marker='o',markersize=5)
                show.ax.plot(x,warning,label="Warning Alram",color='#3a749c',marker='o',markersize=5)
                show.ax.set_title("Weekly Alarm Status")
                show.ax.legend()

                show.canvas.draw()

            if msg_call == "/이미 존재하는 아이디" :
                tkinter.messagebox.showwarning("경고","중복된 아이디입니다")
                show.join_E_mail_Edit.clear()
                show.join_E_mail_Edit.setFocus()

            if msg_call == "/메일 전송 완료" :
                tkinter.messagebox.showinfo("안내","메일 전송이 완료되었습니다")
                show.join_check_code_email = "인증번호 전송완료"

            if "/로그인성공" in msg_call :
                tkinter.messagebox.showinfo("안내","로그인 성공")
                show.login_check = "In"
                data = msg_call.split('*')
                show.user_id = data[1]
                show.user_door_lock = data[2]
                show.user_safe_record = data[3]
                show.user_fake_number = data[4]
                show.user_random_number = data[5]
                show.user_etiquette = data[6]
                if len(data) == 7 :
                    pass
                else :
                    show.user_guest_password = data[7]
                self.Close_LoginForm()

                show.login_msg = 1

                ser.write(f"password {show.user_door_lock}\n".encode())
                time.sleep(0.2)
                ser.write(f"etiquette {show.user_etiquette}\n".encode())
                time.sleep(0.2)
                ser.write(f"fakenumber {show.user_etiquette}\n".encode())
                time.sleep(0.2)
                ser.write(f"record {show.user_safe_record}\n".encode())
                time.sleep(0.2)
                ser.write(f"random {show.user_random_number}\n".encode())

            if msg_call == "/로그인실패" :
                tkinter.messagebox.showwarning("안내","로그인 정보가 옳바르지 않습니다")

            if msg_call == "/인증번호 같지않음" :
                tkinter.messagebox.showwarning("안내","인증번호가 다릅니다")
                show.join_code_Edit.setFocus()

            if msg_call == "/중복 아이디" :
                tkinter.messagebox.showwarning("안내","이미 존재하는 아이디입니다")
                show.join_name_Edit.setFocus()

            if msg_call == "/회원가입 성공" :
                tkinter.messagebox.showinfo("안내","회원가입이 완료되었습니다")
                time.sleep(0.5)
                self.Close_JoinForm()

            if "/도어락 비밀번호 변경 성공" in msg_call :
                tkinter.messagebox.showinfo("안내","도어락 비밀번호 변경이 완료되었습니다")
                show.user_door_lock = msg_call.split("*")[1]
                ser.write(f"passchange {show.user_door_lock}\n".encode())

            if "/게스트 비밀번호 설정 완료" in msg_call :
                tkinter.messagebox.showinfo("안내","게스트 비밀번호 설정 완료")
                show.guset_password_edit.setText("   password")
                show.guset_password_edit.setEchoMode(QLineEdit.Normal)
                show.guset_password_edit.setStyleSheet("color : rgb(191,191,191);"
                                                       "border-style : solid;"
                                                       "border-width : 1px;"
                                                       "border-color : rgb(83,83,83);"
                                                       "border-radius : 15px")
                show.user_guest_password = msg_call.split("*")[1]
                ser.write(f"guestpass {show.user_guest_password}\n".encode())

            if "etiquette" in msg_call :
                ser.write(f"etiquette {msg_call[-1]}\n".encode())

            if "fake_num" in msg_call :
                ser.write(f"fakenumber {msg_call[-1]}\n".encode())

            if "safe_record" in msg_call :
                ser.write(f"record {msg_call[-1]}\n".encode())

            if "random_num" in msg_call :
                ser.write(f"random {msg_call[-1]}\n".encode())

    def Close_LoginForm(self):
        show.login_form.setVisible(False)
        show.trans.close()
        show.login_ID_Edit.clear()
        show.login_PW_Edit.clear()
        show.login_ID_Label.setVisible(True)
        show.login_PW_Label.setVisible(True)

    def Close_JoinForm(self):
        show.join_form.setVisible(False)
        show.login_form.setVisible(True)
        show.join_name_Edit.clear()
        show.join_E_mail_Edit.clear()
        show.join_code_Edit.clear()
        show.join_PW_Edit.clear()
        show.join_Conf_PW_Edit.clear()
        show.join_name_label.setVisible(True)
        show.join_E_mail_label.setVisible(True)
        show.join_code_label.setVisible(True)
        show.join_PW_label.setVisible(True)
        show.join_Conf_PW_label.setVisible(True)
        show.join_PW_info.setVisible(False)
        show.join_Conf_PW_info.setVisible(False)

class Arduino(QThread) :

    recv_data = ""
    doorlock_pw = None

    def run(self):
        while True :
            recv = ser.readline().decode().rstrip()
            print(recv)
            if recv == "None" :
                tkinter.messagebox.showwarning("경고","로그인 이후 사용 가능합니다")
            if recv == "모션감지" :
                show.video_data = "R"
            if recv == "Open" :
                send_data = show.user_id+"*"+"/open"
                sock.send(send_data.encode())
                show.open_msg = 1
            if recv == "Warning" :
                send_data = show.user_id+"*"+"/warning"
                sock.send(send_data.encode())
                show.warning_msg = 1

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    show = MainWindow()
    sys.exit(app.exec_())