import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from plugin.OK2Ship_Gui import OK2Ship_Reviewer_GUI
from PyQt5.QtGui import QIcon

version_id = '0.2.26'
author_id = 'Amazon SQM'

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = OK2Ship_Reviewer_GUI()
    main.show()
    #main.center()

    sys.exit(app.exec_())