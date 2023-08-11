import sys
import warnings
import os

from PyQt5 import QtCore
warnings.simplefilter("ignore",UserWarning)
sys.coinit_flags = 2

import weChatBotModel
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QAction
from PyQt5.QtWidgets import QLabel,QComboBox,QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QCheckBox, QTextEdit
from PyQt5.QtWidgets import QFrame,QStackedLayout,QGridLayout,QFileDialog,QDateTimeEdit,QMessageBox,QMenuBar,QMenu
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication
from weChatBotNet import netWork
import weChatBotData
import keyboard

AUTOREPLY = "自动回复"
KEYWORDREPLY = "关键词自动回复"
TIMEREPLY = "定时回复"
PASS = "无"
#INTELLIGENCEREPLY = "智能回复"

LOGINSIGN = False

## 三个功能页面
class autoReplyGui(QWidget):
    def __init__(self):
        super().__init__()
        self.initui()
        self.autoReplyFunc = None

    def initui(self):
        # 是否开启群聊
        lblGroupChat = QLabel("群聊")
        self.groupChat = QCheckBox("是否开启群聊(默认关闭)")

        # 自动回复内容自定义
        lblAutoReply = QLabel("自动回复内容")
        self.lblAutoReplyContent = QTextEdit()

        gridLayout = QGridLayout()
        gridLayout.addWidget(lblGroupChat,0,0)
        gridLayout.addWidget(self.groupChat,0,1)
        gridLayout.addWidget(lblAutoReply,1,0)
        gridLayout.addWidget(self.lblAutoReplyContent,1,1)

        self.setLayout(gridLayout)
    
    def getObjAndBegin(self,weChatPosition,isGroupCheck):
        self.autoReplyFunc = weChatBotModel.autoReply(
        weChatPath=weChatPosition,
        isGroupChat=isGroupCheck,
        replyContet=self.lblAutoReplyContent.toPlainText()
        )
        self.autoReplyFunc.startFunc()
    
    def end(self):
        if(self.autoReplyFunc):
            self.autoReplyFunc.endFunc()
            return True
        else:
            return False

class keyWordReplyGui(QWidget):
    def __init__(self):
        super().__init__()
        self.initui()
        self.keyWordReplyFunc = None

    def initui(self):
        # 是否开启群聊
        lblGroupChat = QLabel("群聊")
        self.groupChat = QCheckBox("是否开启群聊(默认关闭)")

        # 关键词
        lblKetWord = QLabel("关键词")
        self.lineEditKeyWord = QLineEdit()

        # 回复内容自定义
        lblReply = QLabel("回复内容")
        self.lblReplyContent = QTextEdit()

        gridLayout = QGridLayout()
        gridLayout.addWidget(lblGroupChat,0,0)
        gridLayout.addWidget(self.groupChat,0,1)
        gridLayout.addWidget(lblKetWord,1,0)
        gridLayout.addWidget(self.lineEditKeyWord,1,1)
        gridLayout.addWidget(lblReply,2,0)
        gridLayout.addWidget(self.lblReplyContent,2,1)

        self.setLayout(gridLayout)
    
    def getObjAndBegin(self,weChatPosition,isGroupCheck):
        self.keyWordReplyFunc = weChatBotModel.keyWordReply(
        weChatPath=weChatPosition,
        isGroupChat=isGroupCheck,
        keyWordDict={self.lineEditKeyWord.text():self.lblReplyContent.toPlainText()}
        )
        self.keyWordReplyFunc.startFunc()
    
    def end(self):
        if(self.keyWordReplyFunc):
            self.keyWordReplyFunc.endFunc()
            return True
        else:
            return False

class timeReplyGui(QWidget):
    def __init__(self):
        super().__init__()
        self.initui()
        self.timeReplyFunc = None
    
    def initui(self):
        lblContectMan = QLabel("联系人")
        self.lineEditContectMan = QLineEdit()

        lblReplyContect = QLabel("定时回复内容")
        self.replyContect = QTextEdit()

        lblSelectTime = QLabel("定时")
        self.selectTime = QDateTimeEdit()

        gridLayout = QGridLayout()
        gridLayout.addWidget(lblContectMan,0,0)
        gridLayout.addWidget(self.lineEditContectMan,0,1)
        gridLayout.addWidget(lblSelectTime,1,0)
        gridLayout.addWidget(self.selectTime,1,1)
        gridLayout.addWidget(lblReplyContect,2,0)
        gridLayout.addWidget(self.replyContect,2,1)

        self.setLayout(gridLayout)
    
    def setDataAndGetObj(self,weChatPosition,contect,contectReply,secs):
        self.timeReplyFunc = weChatBotModel.timeReply(
        contectPenson=contect,
        replyContect=contectReply,
        weChatPath=weChatPosition,
        time=secs
        )
        self.timeReplyFunc.startFunc()
    
    def end(self):
        if(self.timeReplyFunc):
            self.timeReplyFunc.startFunc()
            return True
        else:
            return False

## 主页面
class mainWidget(QWidget):
    def __init__(self,menuBar,statusBar):
        super().__init__()
        self.setGetObj = weChatBotData.setGetData()
        self.menuBar = menuBar
        self.statusBar = statusBar
        self.getWeChatPath = None
        self.endTime = None
        self.wechatposition = None
        self.initui()
        self.initData()

    def initui(self):
        #聊天模式以及多选框
        lblModel = QLabel("聊天模式：")

        self.comboModel = QComboBox()
        self.comboModel.activated[str].connect(self.comModelSelected)
        self.comboModel.addItem(AUTOREPLY)
        self.comboModel.addItem(KEYWORDREPLY)
        self.comboModel.addItem(TIMEREPLY)
        #self.comboModel.addItem(INTELLIGENCEREPLY)

        hLayoutModel = QHBoxLayout()
        hLayoutModel.addWidget(lblModel)
        hLayoutModel.addWidget(self.comboModel)
        hLayoutModel.addStretch(2)

        # 微信位置设置以及选择
        weChatPosition = QPushButton("启动微信")
        weChatPosition.clicked.connect(self.openWeChat)

        linePosition1 = QFrame()
        linePosition1.setFrameShape(QFrame.Shape.HLine)
        linePosition1.setFrameShadow(QFrame.Shadow.Plain)

        hLayoutWeChatPosition = QHBoxLayout()
        hLayoutWeChatPosition.addWidget(weChatPosition)

        vLayoutWechatPosition = QVBoxLayout()
        vLayoutWechatPosition.addLayout(hLayoutWeChatPosition)
        vLayoutWechatPosition.addWidget(linePosition1)

        # 开关
        self.beginBtn = QPushButton("开始")
        self.endBtn = QPushButton("结束")
        self.beginBtn.setEnabled(True)
        self.endBtn.setEnabled(False)
        self.beginBtn.clicked.connect(self.beginClick)
        self.endBtn.clicked.connect(self.endClick)

        linePosition2 = QFrame()
        linePosition2.setFrameShape(QFrame.Shape.HLine)
        linePosition2.setFrameShadow(QFrame.Shadow.Plain)

        hLayoutBtn = QHBoxLayout()
        hLayoutBtn.addWidget(self.beginBtn)
        hLayoutBtn.addWidget(self.endBtn)

        vLayoutBtn = QVBoxLayout()
        vLayoutBtn.addWidget(linePosition2)
        vLayoutBtn.addLayout(hLayoutBtn)

        self.stackLayout = QStackedLayout()
        self.autoReplyWidge = autoReplyGui()
        self.keyWordReplyWidge = keyWordReplyGui()
        self.timeReplyWidge = timeReplyGui()
        self.stackLayout.addWidget(self.autoReplyWidge)
        self.stackLayout.addWidget(self.keyWordReplyWidge)
        self.stackLayout.addWidget(self.timeReplyWidge)
        self.stackLayout.setCurrentIndex(3)

        self.vLayout = QVBoxLayout()
        # self.vLayout.addWidget(self.menu)
        self.vLayout.addLayout(hLayoutModel)
        self.vLayout.addLayout(vLayoutWechatPosition)
        self.vLayout.addLayout(self.stackLayout)
        self.vLayout.addLayout(vLayoutBtn)

        self.setLayout(self.vLayout)

    def initData(self):

        # 自动回复设置
        autoReplyData = self.setGetObj.getAutoReplySet()
        self.autoReplyWidge.lblAutoReplyContent.setText(autoReplyData["replyContent"])
        if(autoReplyData["groupChat"]):
            self.autoReplyWidge.groupChat.setCheckState(Qt.CheckState.Checked)
        else:
            self.autoReplyWidge.groupChat.setCheckState(Qt.CheckState.Unchecked)
        
        # 关键词回复
        keyWordReplyData = self.setGetObj.getKeyWordReplySet()
        if(keyWordReplyData["groupChat"]):
            self.keyWordReplyWidge.groupChat.setCheckState(Qt.CheckState.Checked)
        else:
            self.keyWordReplyWidge.groupChat.setCheckState(Qt.CheckState.Unchecked)
        self.keyWordReplyWidge.lineEditKeyWord.setText(keyWordReplyData["keyWord"])
        self.keyWordReplyWidge.lblReplyContent.setText(keyWordReplyData["replyContent"])

        # 定时回复
        timeReplyData = self.setGetObj.getTimeReplySet()
        self.timeReplyWidge.lineEditContectMan.setText(timeReplyData["contect"])
        self.timeReplyWidge.replyContect.setText(timeReplyData["replyContent"])
        timeObj = QDateTime().fromString(timeReplyData["time"])
        self.timeReplyWidge.selectTime.setDateTime(timeObj)
    
    def setData(self):

        # 自动回复设置
        autoReplyData = self.setGetObj.getAutoReplySet()
        autoReplyData["replyContent"] = self.autoReplyWidge.lblAutoReplyContent.toPlainText()
        
        if(self.autoReplyWidge.groupChat.checkState() == Qt.CheckState.Checked):
            autoReplyData["groupChat"] = True
        elif(self.autoReplyWidge.groupChat.checkState() == Qt.CheckState.Unchecked):
            autoReplyData["groupChat"] = False
        else:
            autoReplyData["groupChat"] = False
        self.setGetObj.setAutoReply(autoReplyData)
        
        # 关键词回复
        keyWordReplyData = self.setGetObj.getKeyWordReplySet()
        if(self.keyWordReplyWidge.groupChat.checkState() == Qt.CheckState.Checked):
            keyWordReplyData["gropChat"] = True
        elif(self.keyWordReplyWidge.groupChat.checkState() == Qt.CheckState.Unchecked):
            keyWordReplyData["gropChat"] = False
        else:
            keyWordReplyData["gropChat"] = False
        keyWordReplyData["keyWord"] = self.keyWordReplyWidge.lineEditKeyWord.text()
        keyWordReplyData["replyContent"] = self.keyWordReplyWidge.lblReplyContent.toPlainText()
        self.setGetObj.setKeyWordReply(keyWordReplyData)

        # 定时回复
        timeReplyData = self.setGetObj.getTimeReplySet()
        timeReplyData["contect"] = self.timeReplyWidge.lineEditContectMan.text()
        timeReplyData["replyContent"] = self.timeReplyWidge.replyContect.toPlainText()
        timeObj = self.timeReplyWidge.selectTime.dateTime()
        timeReplyData["time"] = timeObj.toString()
        self.setGetObj.setTimeReply(timeReplyData)

    # 聊天模式选择
    def comModelSelected(self,text):
        if(text == AUTOREPLY):
            self.stackLayout.setCurrentIndex(0)
        elif(text == KEYWORDREPLY):
            self.stackLayout.setCurrentIndex(1)
        elif(text == TIMEREPLY):
            self.stackLayout.setCurrentIndex(2)
    
    # def selectWeChatPosition(self):
    #     weChatPosition = None
    #     if(self.getWeChatPath):
    #         weChatPosition = self.getWeChatPath.getOpenFileUrl()
    #     else:
    #         self.getWeChatPath = QFileDialog(self)
    #         weChatPosition =self.getWeChatPath.getOpenFileUrl()
    #     self.lineEditWeChatPosition.setText(weChatPosition[0].path()[1:])

    # 启动微信
    def openWeChat(self):
        tr = weChatBotModel.Thread(target=self.__openWeChat)
        tr.daemon = True
        tr.start()
    
    def __openWeChat(self):
        currentPath = os.getcwd()
        self.wechatposition = currentPath+"\\wechat\\WeChat.exe"
        os.system(self.wechatposition)

    # 开始开关点击
    def beginClick(self):
        result = weChatBotModel.setWeChatWindow(self.wechatposition)
        if(result):
            pass
        else:
            warningText = str("微信未打开或微信错误，请重新启动微信")
            warningTitle = str("warning")
            QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
            return

        self.beginBtn.setEnabled(False)
        self.endBtn.setEnabled(True)

        index = self.stackLayout.currentIndex()
        if(index == 0):
            isGroupCheck = True if self.autoReplyWidge.groupChat.checkState() == Qt.CheckState.Checked else False
            self.comboModel.setEnabled(False)
            self.autoReplyWidge.getObjAndBegin(
                weChatPosition=self.wechatposition,
                isGroupCheck=isGroupCheck
            )

        elif(index == 1):
            isGroupCheck = True if self.autoReplyWidge.groupChat.checkState() == Qt.CheckState.Checked else False
            self.comboModel.setEnabled(False)
            self.keyWordReplyWidge.getObjAndBegin(
                weChatPosition=self.wechatposition,
                isGroupCheck=isGroupCheck
            )

        elif(index == 2):
            time=self.timeReplyWidge.selectTime.dateTime()
            nowTime = QDateTime.currentDateTime()
            secs = nowTime.secsTo(time)
            if(secs < 0):
                warningText = str("时间设置不能早于现在")
                warningTitle = str("警告")
                QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
                self.beginBtn.setEnabled(True)
                self.endBtn.setEnabled(False)
                return
            
            contect = self.timeReplyWidge.lineEditContectMan.text()
            if(len(contect) == 0):
                warningText = str("联系人不可为空白")
                warningTitle = str("警告")
                QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
                self.beginBtn.setEnabled(True)
                self.endBtn.setEnabled(False)
                return
            
            contectReply = self.timeReplyWidge.replyContect.toPlainText()
            if(len(contectReply) == 0):
                warningText = str("回复内容不可为空白")
                warningTitle = str("警告")
                QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
                self.beginBtn.setEnabled(True)
                self.endBtn.setEnabled(False)
                return
            # warningText = str("设定时间太长，数据溢出")
            # warningTitle = str("警告")
            # QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
            # 启用另一个线程，用于关闭当前功能
            self.endTime = weChatBotModel.Timer(secs,self.endClick)
            self.endTime.daemon = True
            try:
                # 开始执行定时回复的线程
                self.timeReplyWidge.setDataAndGetObj(
                    weChatPosition=self.wechatposition,
                    contect=contect,
                    contectReply=contectReply,
                    secs=secs
                )
                self.endTime.start()
            except:
                return
            self.comboModel.setEnabled(False)
        
        # 启用另一条线程，esc退出
        tr = weChatBotModel.Thread(target=self.inputAndEnd)
        tr.daemon = True
        tr.start()
        self.setData()
    
    # 键入esc暂停功能
    def inputAndEnd(self):
        keyboard.wait('esc')
        self.endClick()
    
    # 点击关闭
    def endClick(self):
        self.beginBtn.setEnabled(True)
        self.endBtn.setEnabled(False)
        self.comboModel.setEnabled(True)
        # 脚本结束运行
        index = self.stackLayout.currentIndex()
        if(index == 0 and self.autoReplyWidge):
            self.autoReplyWidge.end()
        elif(index == 1 and self.keyWordReplyWidge):
            self.keyWordReplyWidge.end()
        elif(index == 2 and self.timeReplyWidge):
            self.timeReplyWidge.end()
            if(self.endTime):
                self.endTime.cancel()
        else:
            self.beginBtn.setEnabled(True)
            self.endBtn.setEnabled(False)
            self.comboModel.setEnabled(False)

## 账密的登录
class loginWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        pass

    def initUI(self):
        self.lineEditEmail = QLineEdit()
        lblEmail = QLabel("邮箱")

        self.lineEditPassWord = QLineEdit()
        self.lineEditPassWord.setEchoMode(QLineEdit.EchoMode.Password)
        self.lineEditPassWord.setMaxLength(12)
        lblPassWord = QLabel("密码")

        emailLayout = QHBoxLayout()
        emailLayout.addWidget(lblEmail)
        emailLayout.addWidget(self.lineEditEmail)

        passwordLayout = QHBoxLayout()
        passwordLayout.addWidget(lblPassWord)
        passwordLayout.addWidget(self.lineEditPassWord)

        self.vLayout = QVBoxLayout()
        self.vLayout.addLayout(emailLayout)
        self.vLayout.addLayout(passwordLayout)

        self.setLayout(self.vLayout)

## 注册账号
class registerWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self):
        self.lineEditEmail = QLineEdit()
        lblEmail = QLabel("邮箱")

        self.lineEditPassWord = QLineEdit()
        lblPassWord = QLabel("验证码")

        emailLayout = QHBoxLayout()
        emailLayout.addWidget(lblEmail)
        emailLayout.addWidget(self.lineEditEmail)

        passwordLayout = QHBoxLayout()
        passwordLayout.addWidget(lblPassWord)
        passwordLayout.addWidget(self.lineEditPassWord)

        self.vLayout = QVBoxLayout()
        self.vLayout.addLayout(emailLayout)
        self.vLayout.addLayout(passwordLayout)

        self.setLayout(self.vLayout)

## 登录页面
class loginMainWidget(QWidget):
    def __init__(self,callback) -> None:
        super().__init__()
        try:
            self.netObj = netWork()
        except:
            self.netObj = None
        self.callback = callback
        self.setWindowTitle("登录")
        self.initUI()

    def initUI(self):
        self.login = loginWidget()
        self.regist = registerWidget()

        self.stackLayout = QStackedLayout()
        self.stackLayout.addWidget(self.login)
        self.stackLayout.addWidget(self.regist)

        if self.stackLayout.currentIndex() == 0:
            self.loginBtn = QPushButton("登录")
            self.switchWidgetBtn = QPushButton("注册")
            self.setWindowTitle("登录")
        else:
            self.loginBtn = QPushButton("确认")
            self.switchWidgetBtn = QPushButton("登录")
            self.setWindowTitle("注册")

        self.switchWidgetBtn.clicked.connect(self.switchWidgetBtnClick)
        self.cancelBtn = QPushButton("取消")
        self.cancelBtn.clicked.connect(self.cancelBtnClick)
        self.changePassWord = QPushButton("忘记密码")
        
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.loginBtn)
        btnLayout.addWidget(self.cancelBtn)
        btnLayout.addWidget(self.changePassWord)
        btnLayout.addWidget(self.switchWidgetBtn)

        self.vlayout = QVBoxLayout()
        self.vlayout.addLayout(self.stackLayout)
        self.vlayout.addLayout(btnLayout)

        self.setLayout(self.vlayout)
    
    def loginBtnClick(self):
        if(self.stackLayout.currentIndex() == 0):
            inner_email = self.login.lineEditEmail.text()
            inner_password = self.login.lineEditPassWord.text()
            if(self.netObj):
                receData = self.netObj.login(inner_email,inner_password)
                self.callback(receData)
                self.close()
            else:
                warningText = str("服务错误，未能连接服务器")
                warningTitle = str("警告")
                QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
        else:
            inner_email = self.login.lineEditEmail.text()
            inner_password = self.login.lineEditPassWord.text()
            if(self.netObj):
                receData = self.netObj.login(inner_email,inner_password)
                if(receData):
                    self.callback(receData)
                    self.close()
                else:
                    warningText = str("编码错误")
                    warningTitle = str("警告")
                    QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
            else:
                warningText = str("网络错误，无法连接服务器")
                warningTitle = str("警告")
                QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)

    def cancelBtnClick(self):
        self.close()

    def changePassWordBtnClick(self):
        pass

    def switchWidgetBtnClick(self):
        if (self.stackLayout.currentIndex() == 0):
            self.stackLayout.setCurrentIndex(1)
            self.loginBtn.setText("确认")
            self.switchWidgetBtn.setText("登录")
            self.setWindowTitle("注册")
        else:
            self.stackLayout.setCurrentIndex(0)
            self.loginBtn.setText("登录")
            self.switchWidgetBtn.setText("注册")
            self.setWindowTitle("登录")

## 个人中心
class personnalPageWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self):
        pass

## 主窗口
class mainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        try:
            self.netObj = netWork()
            self.netObj.getLoginStatus(self.initMenuCallback)
        except:
            warningText = str("网络错误，未能链接服务器")
            warningTitle = str("警告")
            QMessageBox.warning(self,warningTitle,warningText,QMessageBox.StandardButton.Ok)
        
        self.initMenuCallback(True)
        self.mainWidget = mainWidget(self.menuBar(),self.statusBar())
        self.setCentralWidget(self.mainWidget)
    
    def initMenuCallback(self,result):
        if(result):
            self.initMenuWithLogin()
        else:
            self.initMenuWithNoLogin()

    def initMenuWithNoLogin(self):
        menuBar = self.menuBar()
        listMenu = menuBar.addMenu("菜单")
        ac = QAction("未登录",self)
        ac.triggered.connect(self.noLoginAction)
        listMenu.addAction(ac)

    def initMenuWithLogin(self):
        menuBar = self.menuBar()
        listMenu = menuBar.addMenu("菜单")
        ac = QAction("个人中心",self)
        ac.triggered.connect(self.loginAction)
        listMenu.addAction(ac)
    
    def noLoginAction(self):
        status = self.statusBar()
        status.showMessage("打开登陆页面")
    
    def loginAction(self):
        status = self.statusBar()
        status.showMessage("打开个人中心")
        self.loginW = loginMainWidget(self.initMenuCallback)
        self.loginW.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.loginW.show()
