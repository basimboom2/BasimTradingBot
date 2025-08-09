
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core import auth
from gui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - Basim Trading Bot")
        self.resize(400, 350)
        self.current_lang = "ar"
        self.dark_mode = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # عنوان
        self.title_label = QLabel("🪙 Basim Trading Bot")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # حقل اسم المستخدم
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم" if self.current_lang == "ar" else "Username")
        layout.addWidget(self.username_input)

        # حقل كلمة المرور
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور" if self.current_lang == "ar" else "Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # زر إظهار/إخفاء كلمة المرور
        self.toggle_pass_btn = QPushButton("👁")
        self.toggle_pass_btn.setFixedWidth(40)
        self.toggle_pass_btn.clicked.connect(self.toggle_password)
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.toggle_pass_btn)

        # أزرار التحكم
        btn_layout = QHBoxLayout()

        self.login_btn = QPushButton("دخول" if self.current_lang == "ar" else "Login")
        self.login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(self.login_btn)

        self.lang_btn = QPushButton("EN" if self.current_lang == "ar" else "AR")
        self.lang_btn.clicked.connect(self.toggle_language)
        btn_layout.addWidget(self.lang_btn)

        self.theme_btn = QPushButton("🌙" if not self.dark_mode else "☀️")
        self.theme_btn.clicked.connect(self.toggle_theme)
        btn_layout.addWidget(self.theme_btn)

        layout.addLayout(btn_layout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)
        self.apply_theme()

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
        self.lang_btn.setText("EN" if self.current_lang == "ar" else "AR")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("🌙" if not self.dark_mode else "☀️")
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: #121212; color: white;")
        else:
            self.setStyleSheet("")

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "خطأ" if self.current_lang == "ar" else "Error",
                                "الرجاء إدخال اسم المستخدم وكلمة المرور" if self.current_lang == "ar" else "Please enter username and password")
            return

        # التحقق من تسجيل الدخول عبر auth.py
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
