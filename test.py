from QtUI.EmojiDialog import EmojiDialog
import sys
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
window = EmojiDialog()


window.show()
print(window.selectEmoji)
sys.exit(app.exec_())
