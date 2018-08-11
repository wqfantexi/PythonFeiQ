from .FeiQ import Ui_MainWindow
from PyQt5 import QtWidgets
import sys
from socketserver import UDPServer, ThreadingUDPServer
from FeiQ.SocketHandle import UdpHandle
from FeiQ.WorkThread import Instance
import socket
from FeiQ.UserManager import *
from QtUI.Widget import *
from FeiQ.View.View import ViewType
from FeiQ.Struct.PacketContent import ContentType
from FeiQ.Struct.TextContent import TextContent
from QtUI.EmojiDialog import EmojiDialog

class FeiQMainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    _contentSignal = pyqtSignal(PacketContent)
    _userSignal = pyqtSignal(User)
    def __init__(self):
        super(FeiQMainWindow, self).__init__()
        self.setupUi(self)

        #http://10.78.13.168/newtdmantis/view.php?id=1131638
        #file:///D:/WorkSpace/PythonFeiQ/static/html/chatDialog.html
        #self.chatHistory.load(QUrl('http://10.78.13.168/newtdmantis/view.php?id=1131638'))
        #self.chatHistory.show()
        self.dataFriend = ListFriendModel()
        self.listFriend.setViewMode(QtWidgets.QListView.ListMode)

        self.listFriend.setModel(self.dataFriend)
        self.listFriend.setStyleSheet("QListView{icon-size:70px}")

        self.dataChat = ListFriendModel()
        self.listChat.setViewMode(QtWidgets.QListView.ListMode)

        self.listChat.setModel(self.dataChat)
        self.listChat.setStyleSheet("QListView{icon-size:70px}")

        self.listFriend.setItemDelegate(FriendDelegate(self))
        self.listChat.setItemDelegate(FriendDelegate(self))

        self.currentUser = None

        self._contentSignal.connect(self.dealRecgvContent)
        self._userSignal.connect(self.dealRecvUser)

        #先备份原始的按键消息，然后捕获系统按键消息
        self.originKeyPressEvnet = self.textEdit.keyPressEvent
        self.textEdit.keyPressEvent=self.onEvent

    #捕获用户enter按键消息
    def onEvent(self, keyevent:QKeyEvent):
        key = keyevent.key()
        #如果是ctrl+enter，那么转发enter消息到原始的消息处理中
        if (key == Qt.Key_Enter or key == Qt.Key_Return) and Qt.ControlModifier & keyevent.modifiers():
            newEvent=QKeyEvent(6, Qt.Key_Return, Qt.NoModifier)
            self.originKeyPressEvnet(newEvent)
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            self.onSendMessage()
        else:
            self.originKeyPressEvnet(keyevent)

    def onFriendDbClick(self, itemIndex):
        find = self.dataFriend.getItem(itemIndex.row())
        if find is None:
            return
        self.moveFriendToChatList(find, True)

    #用户点击了聊天列表
    def onClickChatItem(self, itemIndex):
        find = self.dataChat.getItem(itemIndex.row())
        if find is self.currentUser:
            return
        if find is None:
            return
        self.BeginChat(find)

    #将用户从联系人列表加载到聊天列表
    #beginChat = true,用户主动点击，需要开始进行聊天；否则是后台接收消息，把用户放入聊天列表即可
    def moveFriendToChatList(self, user, beginChat):
        if user is self.currentUser:
            if beginChat:#如果是主动点击，切换tab
                self.tabWidget.setCurrentIndex(0)
            return
        self.dataChat.updatefirst(user)

        if beginChat:
            index = self.dataChat.index(0)
            self.listChat.setCurrentIndex(index)
            self.tabWidget.setCurrentIndex(0)

            self.BeginChat(user)

    #开始聊天，设置各种参数，加载聊天历史
    def BeginChat(self, user):
        self.currentUser = user
        self.setChatTitle('与%s(%s)聊天中...' % (user.nickname, user.groupname))
        self.setChatHistory()

    #设置聊天窗口内容
    def setChatTitle(self, msg):
        self.chatTitle.setText(msg)

    #把聊天记录历史显示出来
    def setChatHistory(self):
        self.textBrowser.clear()
        for item in self.currentUser.lstContents:
            if item.tx:
                self.setSelfMessage(item)
            else:
                self.setPeerMessage(item)

    #显示对方输入内容
    def setPeerMessage(self, content:PacketContent):
        self.textBrowser.append('<span style="float:right;text-align:right;"><font size="5">%s</font><font size="3">%s</font></span>'%(self.currentUser.nickname+'\t', content.time.strftime('%Y-%m-%d %H:%M:%S')))
        if content.type == ContentType.TEXT:
            content.DealBeforeShow() #在显示前把图片替换
            self.textBrowser.append('<span style="float:right;text-align:right;">%s</span>'%content.text)

    #显示我方输入内容
    def setSelfMessage(self, content:PacketContent):
        self.textBrowser.append(
            '<font size="5">%s</font><font size="3">%s</font>' % ('我\t', content.time.strftime('%Y-%m-%d %H:%M:%S')))
        if content.type == ContentType.TEXT:
            self.textBrowser.append('<span>%s</span>'%content.text)


    #发送聊天内容
    def onSendMessage(self):
        text = self.textEdit.toPlainText()
        if len(text) == 0:
            return
        if self.currentUser is None:
            return
        content = TextContent(text, '', self.currentUser.getId(), True)
        self.textEdit.clear()

        Instance.appendContent(content)

        self.setSelfMessage(content)


    #这个是实际处理的函数
    def dealRecgvContent(self, content):
        if self.currentUser is not None and content.peer == self.currentUser.getId():
            self.setPeerMessage(content)
        else:
            user = self.dataFriend.find(content.peer)
            if user is not None:
                self.moveFriendToChatList(user, False)

    #设置消息回调
    def onContentRecv(self, content):
        self._contentSignal.emit(content)

    def dealRecvUser(self,user):
        self.dataFriend.updateItem(user)


    #处理后台发送的各种消息，所有从后台到来的消息统一从这里分发
    def onViewDispatch(self, view):
        if view.type() == ViewType.VIEW_USER:
            self._userSignal.emit(view.user)
        elif view.type() == ViewType.VIEW_CONTENT:
            self._contentSignal.emit(view.content)

    #打开表情选择对话框
    def onClickEmoji(self):
        emojiDlg = EmojiDialog()
        emojiDlg.exec_()
        print(emojiDlg.selectEmoji)

        img = '<img src=\"%s\"></img>' % emojiDlg.selectEmoji.path
        self.textEdit.append(img)

    #打开图片选择界面
    def onClickImage(self):
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = FeiQMainWindow()

    UDPSERVER = ThreadingUDPServer((setting.IPADDRESS, setting.PORT), UdpHandle)
    UDPSERVER.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UDPSERVER.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 60000)

    serverMainThread = threading.Thread(target=UDPSERVER.serve_forever, name='后台主线程')
    serverMainThread.setDaemon(True)
    serverMainThread.start()
    Instance.start(UDPSERVER.socket.sendto, window.onViewDispatch)

    window.show()
    sys.exit(app.exec_())
    UDPSERVER.server_close()
    Instance.stopAll()
