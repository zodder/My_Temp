import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from plugin.Main_GUI_PyQT5 import CTDA_MainWindow
from PyQt5.QtGui import QIcon

version_id = '0.2.26'
author_id = 'Amazon SQM'

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = CTDA_MainWindow(version_id=version_id, author_id=author_id)
    main.show()
    #main.center()

    sys.exit(app.exec_())
