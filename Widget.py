from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading

class ListFriendModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.ListItemData = []
        CollectionLock: threading.Lock = threading.Lock()  # 容器锁

    def data(self, index, role):
        if index.isValid() or (0 <= index.row() < len(self.ListItemData)):
            row = index.row()
            if role == Qt.DisplayRole:
                return QVariant(self.ListItemData[row].nickname)
            elif role == Qt.ToolTipRole:
                return QVariant(self.ListItemData[row].groupname)
            elif role == Qt.DecorationRole:
                return QVariant(QIcon(self.ListItemData[row].headpic))
            elif role == Qt.SizeHintRole:
                return QVariant(QSize(70, 80))
            elif role == Qt.TextAlignmentRole:
                return QVariant(int(Qt.AlignHCenter | Qt.AlignVCenter))
            elif role == Qt.FontRole:
                font = QFont()
                font.setPixelSize(20)
                return QVariant(font)
            elif role == Qt.UserRole + 1: #登录名
                return QVariant(self.ListItemData[row].loginname)
            elif role == Qt.UserRole + 2: #电脑名
                return QVariant(self.ListItemData[row].hostname)
            elif role == Qt.UserRole + 3: #分组名
                return QVariant(self.ListItemData[row].groupname)
            elif role == Qt.UserRole + 4: #IP地址
                return QVariant(self.ListItemData[row].ip +'@'+ str(self.ListItemData[row].port))

        else:
            return QVariant()


    def rowCount(self, parent=QModelIndex()):
        return len(self.ListItemData)


    #def addItem(self, itemData):
    #    #self.CollectionLock.acquire()
    #    if itemData:
    #        self.beginInsertRows(QModelIndex(), len(self.ListItemData), len(self.ListItemData) + 1)
    #        self.ListItemData.append(itemData)
    #        self.endInsertRows()
    #    #self.CollectionLock.release()

    def deleteItem(self, index):
        del self.ListItemData[index]


    def getItem(self, index):
        if index > -1 and index < len(self.ListItemData):
            return self.ListItemData[index]

    def updateItem(self, item):
        #self.CollectionLock.acquire()
        self.beginInsertRows(QModelIndex(), len(self.ListItemData), len(self.ListItemData) + 1)
        find = next((x for x in self.ListItemData if x.getId() == item.getId()), None)
        if find is None:
            self.ListItemData.append(item)
        else:
            find.update(item)
        self.endInsertRows()
        #self.CollectionLock.release()
    # 插入到第一个位置
    def updatefirst(self, item):
        #self.CollectionLock.acquire()
        find = next((x for x in self.ListItemData if x.getId() == item.getId()), None)
        self.beginInsertRows(QModelIndex(), len(self.ListItemData), len(self.ListItemData) + 1)
        if find is not None:
            self.ListItemData.remove(find)

        self.ListItemData.insert(0, item)
        self.endInsertRows()
        #self.CollectionLock.release()

    def find(self,id):
        find = next((x for x in self.ListItemData if x.getId() == id), None)
        return find
class FriendDelegate(QItemDelegate):
    def __init__(self, parent=None, *args):
        QItemDelegate.__init__(self, parent, *args)

    def paint(self, painter:QPainter, option, index):
        painter.save()

        # set background color
        painter.setPen(QPen(Qt.NoPen))
        if option.state & QStyle.State_Selected:
            painter.setBrush(QBrush(Qt.red))
        else:
            painter.setBrush(QBrush(Qt.white))
        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QPen())
        painter.setPen(QPen(Qt.black))
        nickName = index.data(Qt.DisplayRole)
        groupname = index.data(Qt.UserRole + 3)

        top=option.rect.top()

        nameRect = QRect(80,5+top,123,20)
        painter.drawText(nameRect, Qt.AlignLeft, nickName)

        groupRect = QRect(80, 35 + top, 123, 20)
        painter.drawText(groupRect, Qt.AlignLeft, groupname)

        loginname = index.data(Qt.UserRole + 1)
        hostname = index.data(Qt.UserRole + 2)
        pcRect = QRect(80, 50+top, 123, 20)
        painter.drawText(pcRect, Qt.AlignLeft, '%s (%s)' % (loginname, hostname))

        addr = index.data(Qt.UserRole + 4)
        addrRect = QRect(80, 65+top, 123, 20)
        painter.drawText(addrRect, Qt.AlignLeft, addr)

        icon : QIcon = index.data(Qt.DecorationRole)
        if icon is not None:
            iconRect = QRect(5,5+top,70,70)
            icon.paint(painter, iconRect)

        painter.restore()