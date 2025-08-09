
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from core import auth
from gui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - Basim Trading Bot")
        self.resize(420, 400)
        self.current_lang = "ar"
        self.dark_mode = False
        self.init_ui()
        self.center()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # عنوان
        self.title_label = QLabel("🪙 Basim Trading Bot")
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # حقل اسم المستخدم
        user_layout = QHBoxLayout()
        user_icon = QLabel("👤")
        user_icon.setFont(QFont("Segoe UI", 14))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم" if self.current_lang == "ar" else "Username")
        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.username_input)
        layout.addLayout(user_layout)

        # حقل كلمة المرور
        pass_layout = QHBoxLayout()
        pass_icon = QLabel("🔒")
        pass_icon.setFont(QFont("Segoe UI", 14))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور" if self.current_lang == "ar" else "Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.toggle_pass_btn = QPushButton("👁")
        self.toggle_pass_btn.setFixedWidth(40)
        self.toggle_pass_btn.clicked.connect(self.toggle_password)
        pass_layout.addWidget(pass_icon)
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.toggle_pass_btn)
        layout.addLayout(pass_layout)

        # أزرار التحكم
        top_btns = QHBoxLayout()
        self.lang_btn = QPushButton("🌐")
        self.lang_btn.clicked.connect(self.toggle_language)
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_btns.addWidget(self.lang_btn)
        top_btns.addWidget(self.theme_btn)
        layout.addLayout(top_btns)

        # زر دخول
        self.login_btn = QPushButton("دخول" if self.current_lang == "ar" else "Login")
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)
        self.apply_theme()

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

    def toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        self.username_input.setPlaceholderText("اسم المستخدم" if self.current_lang == "ar" else "Username")
        self.password_input.setPlaceholderText("كلمة المرور" if self.current_lang == "ar" else "Password")
        self.login_btn.setText("دخول" if self.current_lang == "ar" else "Login")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("🌙" if not self.dark_mode else "☀️")
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: #1e1e1e; color: white;")
        else:
            self.setStyleSheet("")

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "خطأ" if self.current_lang == "ar" else "Error",
                                "الرجاء إدخال اسم المستخدم وكلمة المرور" if self.current_lang == "ar" else "Please enter username and password")
            return

        status, message = auth.login(username, password)
        if status == "success":
            self.open_main_window(username)
        else:
            QMessageBox.critical(self, "خطأ" if self.current_lang == "ar" else "Error", message)

    def open_main_window(self, username):
        self.main_win = MainWindow(username)
        self.main_win.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
