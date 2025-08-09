
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core import auth
from gui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self, lang="ar"):
        super().__init__()
        self.lang = lang
        self.dark_mode = True  # الوضع الافتراضي داكن
        self.setWindowTitle("Basim Trading Bot — تسجيل الدخول" if lang == "ar" else "Basim Trading Bot - Login")
        self.resize(460, 360)
        self._build_ui()
        self._apply_styles()
        self.center()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        # العنوان
        self.title = QLabel("🪙 Basim Trading Bot")
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # الوصف
        self.subtitle = QLabel("الرجاء تسجيل الدخول للمتابعة" if self.lang == "ar" else "Please sign in to continue")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.subtitle)

        layout.addSpacerItem(QSpacerItem(20, 6, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # حقل اسم المستخدم
        user_row = QHBoxLayout()
        user_icon = QLabel("👤")
        user_icon.setFont(QFont("Segoe UI", 14))
        user_row.addWidget(user_icon)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم" if self.lang == "ar" else "Username")
        user_row.addWidget(self.username_input)
        layout.addLayout(user_row)

        # حقل كلمة المرور
        pass_row = QHBoxLayout()
        pass_icon = QLabel("🔒")
        pass_icon.setFont(QFont("Segoe UI", 14))
        pass_row.addWidget(pass_icon)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور" if self.lang == "ar" else "Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        pass_row.addWidget(self.password_input)
        toggle_pass_btn = QPushButton("👁")
        toggle_pass_btn.setFixedWidth(36)
        toggle_pass_btn.clicked.connect(self._toggle_password)
        pass_row.addWidget(toggle_pass_btn)
        layout.addLayout(pass_row)

        # أزرار التحكم
        row_btns = QHBoxLayout()
        self.lang_btn = QPushButton("EN" if self.lang == "ar" else "AR")
        self.lang_btn.setFixedSize(50, 32)
        self.lang_btn.clicked.connect(self._toggle_language)
        row_btns.addWidget(self.lang_btn)

        self.theme_btn = QPushButton("☀️" if self.dark_mode else "🌙")
        self.theme_btn.setFixedSize(34, 32)
        self.theme_btn.clicked.connect(self._toggle_theme)
        row_btns.addWidget(self.theme_btn)
        row_btns.addStretch()
        layout.addLayout(row_btns)

        # زر الدخول
        self.login_btn = QPushButton("دخول" if self.lang == "ar" else "Login")
        self.login_btn.setFixedHeight(42)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_btn.clicked.connect(self._on_login_clicked)
        layout.addWidget(self.login_btn)

        # الرسالة
        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.msg_label)

        self.setLayout(layout)

        # التنقل بالـ Enter
        self.username_input.returnPressed.connect(self._focus_password)
        self.password_input.returnPressed.connect(self._on_login_clicked)

    def _apply_styles(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #0f172a;
                    color: #f3f4f6;
                }
                QLabel { color: #e2e8f0; }
                QLineEdit {
                    background: rgba(255,255,255,0.06);
                    border: 1px solid rgba(255,255,255,0.1);
                    padding: 6px;
                    border-radius: 6px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f1f5f9;
                    color: #1e293b;
                }
                QLabel { color: #1e293b; }
                QLineEdit {
                    background: white;
                    border: 1px solid #cbd5e1;
                    padding: 6px;
                    border-radius: 6px;
                    color: #1e293b;
                }
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def _toggle_language(self):
        self.lang = "en" if self.lang == "ar" else "ar"
        self.username_input.setPlaceholderText("اسم المستخدم" if self.lang == "ar" else "Username")
        self.password_input.setPlaceholderText("كلمة المرور" if self.lang == "ar" else "Password")
        self.login_btn.setText("دخول" if self.lang == "ar" else "Login")
        self.lang_btn.setText("EN" if self.lang == "ar" else "AR")
        self.subtitle.setText("الرجاء تسجيل الدخول للمتابعة" if self.lang == "ar" else "Please sign in to continue")
        self.setWindowTitle("Basim Trading Bot — تسجيل الدخول" if self.lang == "ar" else "Basim Trading Bot - Login")

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_styles()
        self.theme_btn.setText("☀️" if self.dark_mode else "🌙")

    def _focus_password(self):
        self.password_input.setFocus()

    def _on_login_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.msg_label.setText("الرجاء إدخال اسم المستخدم وكلمة المرور" if self.lang=="ar" else "Please enter username and password")
            return

        try:
            result = auth.login(username, password)
        except Exception:
            self.msg_label.setText("خطأ في الاتصال" if self.lang=="ar" else "Connection error")
            return

        status = result.get("status")
        role = result.get("role", "user")

        if status == "success":
            self.open_main_window(username, role)
        elif status == "pending":
            self.msg_label.setText("طلبك قيد الموافقة" if self.lang=="ar" else "Pending approval")
        else:
            self.msg_label.setText("بيانات الدخول غير صحيحة" if self.lang=="ar" else "Invalid credentials")

    def open_main_window(self, username, role="user"):
        self.main_win = MainWindow(username=username, role=role, lang=self.lang)
        self.main_win.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
