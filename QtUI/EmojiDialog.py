from QtUI.Emoji import Ui_Dialog
from PyQt5 import QtWidgets
import sys
from PyQt5.QtCore import QAbstractTableModel,QModelIndex,QVariant,Qt
from PyQt5 import QtGui
from PyQt5 import QtCore
from FeiQ.Config import setting
from collections import namedtuple
import glob
import os

EmojiItem = namedtuple('EmojiItem', ['system','key','path'])
EmojiGroup = namedtuple('EmojiGroup',['name','size','data'])


class EmojiManager:
    def __init__(self):
        self.emoji = []
        self.loadFromSetting()

    def loadFromSetting(self):
        for category in setting.emoji:
            basePath = category['path']
            lst = []
            if category['system']: #系统图标
                for item in category['data']:
                    lst.append(EmojiItem._make([category['system'], item['key'], basePath + item['filename']]))
            else:
                files = glob.glob(basePath + '*')
                for item in files:
                    tmp,filename = os.path.split(item)
                    lst.append(EmojiItem._make([False, filename, item]))

            group = EmojiGroup(name=category['name'], size=category['size'],data=lst)

            self.emoji.append(group)

#定义显示的数据模型
class MyEmojiModel(QAbstractTableModel):
    def __init__(self, lstEmoji, widthNo, parent=None):
        super(MyEmojiModel, self).__init__(parent)

        self.gifData = lstEmoji
        self.COLWIDTH = widthNo

    def rowCount(self, QModelIndex):
        lens = len(self.gifData)
        if lens % self.COLWIDTH == 0:
            return lens / self.COLWIDTH
        else:
            return int(lens / self.COLWIDTH + 1)

    def columnCount(self, QModelIndex):
        return self.COLWIDTH

    def data(self, index: QtCore.QModelIndex, role):
        row = index.row()
        col = index.column()
        lens = len(self.gifData)

        idx = row * self.COLWIDTH + col
        if idx >= lens:
            return QVariant()

        if role == Qt.DisplayRole:
            return self.gifData[idx]
        return QVariant()

#显示图标的delegate
class ShowIconDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(ShowIconDelegate, self).__init__(parent)
        self.dictWidget = dict()

    def paint(self, painter: QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        emoji: EmojiItem = index.data(Qt.DisplayRole)
        if index in self.dictWidget:
            return

        #print(icon)
        if emoji is not None:
            movie = QtGui.QMovie(emoji.path)
            movie.setCacheMode(QtGui.QMovie.CacheAll)
            movie.setSpeed(100)

            label = QtWidgets.QLabel()
            #label.setText(icon)
            label.setMovie(movie)

            self.parent().setIndexWidget(
                index,
                label
            )
            self.dictWidget[index] = label
            movie.start()

class EmojiDialog(QtWidgets.QDialog,Ui_Dialog):
    def __init__(self):
        super(EmojiDialog, self).__init__()
        emojiMgr = EmojiManager()
        self.setupUi(self)
        self.setFixedSize(520,320)
        self.selectEmoji = None

        for group in emojiMgr.emoji:
            tab = QtWidgets.QWidget()
            tab.setObjectName(group.name)
            gridLayout_3 = QtWidgets.QGridLayout(tab)
            gridLayout_3.setContentsMargins(1, 1, 1, 1)
            gridLayout_3.setObjectName("gridLayout_" + group.name)

            tableView = QtWidgets.QTableView(tab)
            tableView.setObjectName("tableView" + group.name)
            gridLayout_3.addWidget(tableView, 0, 0, 1, 1)
            self.tabWidget.addTab(tab, "")
            _translate = QtCore.QCoreApplication.translate
            self.tabWidget.setTabText(self.tabWidget.indexOf(tab), _translate("Dialog", group.name))

            widthNo = int(498 / group.size) #一排表情数量

            tableView.horizontalHeader().setDefaultSectionSize(group.size)
            tableView.verticalHeader().setDefaultSectionSize(group.size)
            tableView.horizontalHeader().setVisible(False) #隐藏表头
            tableView.verticalHeader().setVisible(False) #隐藏表头
            delegate = ShowIconDelegate(tableView)
            tableView.setItemDelegate(delegate)

            tableView.clicked['QModelIndex'].connect(self.onClickFunc)

            model = MyEmojiModel(group.data, widthNo)
            tableView.setModel(model)

    #单元格点击事件
    def onClickFunc(self,index: QtCore.QModelIndex):
        emoji: EmojiItem = index.data(Qt.DisplayRole)
        if emoji is None:
            return
        # if emoji.system:
        #     print(emoji.key)
        # else:
        #     print(emoji.path)

        self.selectEmoji = emoji

        self.close()
        #self.setVisible(False)
