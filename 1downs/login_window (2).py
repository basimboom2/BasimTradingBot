
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
from core import auth
from gui.main_window import MainWindow

class LoginWindow(QWidget):
    """
    واجهة تسجيل دخول عصرية ومُحسّنة:
    - خلفية متدرجة بسيطة
    - أيقونات بجانب الحقول
    - تبديل اللغة (AR/EN) + الوضع الليلي
    - تنقّل بالـ Enter: من اليوزر للباسورد، ومن الباسورد ينفّذ الدخول
    - ربط مباشر بدالة auth.login (تستخدم دوال المشروع الحالية)
    - عند نجاح الدخول تفتح MainWindow مع نقل اسم المستخدم والدور
    """

    def __init__(self, lang="ar"):
        super().__init__()
        self.setWindowTitle("Basim Trading Bot — تسجيل الدخول" if lang == "ar" else "Basim Trading Bot - Login")
        self.resize(520, 420)
        self.lang = lang  # "ar" or "en"
        self.dark_mode = False
        self._build_ui()
        self._apply_styles()
        self.center()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        # Title / banner
        self.title = QLabel("🪙 Basim Trading Bot")
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        layout.addSpacerItem(QSpacerItem(20, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Subtitle / hint
        self.subtitle = QLabel("الرجاء تسجيل الدخول للمتابعة" if self.lang == "ar" else "Please sign in to continue")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.subtitle)

        layout.addSpacerItem(QSpacerItem(20, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Username row
        user_row = QHBoxLayout()
        user_icon = QLabel("👤")
        user_icon.setFont(QFont("Segoe UI", 14))
        user_row.addWidget(user_icon)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم" if self.lang == "ar" else "Username")
        self.username_input.setObjectName("username_input")
        user_row.addWidget(self.username_input)
        layout.addLayout(user_row)

        # Password row
        pass_row = QHBoxLayout()
        pass_icon = QLabel("🔒")
        pass_icon.setFont(QFont("Segoe UI", 14))
        pass_row.addWidget(pass_icon)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور" if self.lang == "ar" else "Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("password_input")
        pass_row.addWidget(self.password_input)
        self.toggle_pass_btn = QPushButton("👁")
        self.toggle_pass_btn.setFixedWidth(40)
        self.toggle_pass_btn.clicked.connect(self._toggle_password)
        pass_row.addWidget(self.toggle_pass_btn)
        layout.addLayout(pass_row)

        # Buttons row (theme + lang + login)
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.addStretch()

        self.lang_btn = QPushButton("EN" if self.lang == "ar" else "AR")
        self.lang_btn.setFixedSize(52, 34)
        self.lang_btn.clicked.connect(self._toggle_language)
        top_row.addWidget(self.lang_btn)

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(34, 34)
        self.theme_btn.clicked.connect(self._toggle_theme)
        top_row.addWidget(self.theme_btn)

        layout.addLayout(top_row)

        layout.addSpacerItem(QSpacerItem(20, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Login button
        self.login_btn = QPushButton("دخول" if self.lang == "ar" else "Login")
        self.login_btn.setFixedHeight(44)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_btn.clicked.connect(self._on_login_clicked)
        layout.addWidget(self.login_btn)

        # message label
        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.msg_label)

        # Footer spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        # Keyboard behavior: Enter to move/focus or submit
        self.username_input.returnPressed.connect(self._focus_password)
        self.password_input.returnPressed.connect(self._on_login_clicked)

    def _apply_styles(self):
        # Gradient background + basic styling. Can be extended later.
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1,
                              stop:0 #0f172a, stop:1 #0b8793);
                color: #f3f4f6;
            }
            QLabel { color: #e6eef0; }
            QLineEdit {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.08);
                padding: 8px;
                border-radius: 6px;
                color: #ffffff;
            }
            QPushButton#login_btn {
                background: #10b981;
                color: white;
                border-radius: 8px;
            }
        """)
        # Style login button specifically
        self.login_btn.setStyleSheet("background-color: #10b981; color: white; border-radius: 8px;")

    def center(self):
        # center the window on the primary screen
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
        # update placeholders and labels
        self.username_input.setPlaceholderText("اسم المستخدم" if self.lang == "ar" else "Username")
        self.password_input.setPlaceholderText("كلمة المرور" if self.lang == "ar" else "Password")
        self.login_btn.setText("دخول" if self.lang == "ar" else "Login")
        self.lang_btn.setText("EN" if self.lang == "ar" else "AR")
        self.subtitle.setText("الرجاء تسجيل الدخول للمتابعة" if self.lang == "ar" else "Please sign in to continue")
        self.setWindowTitle("Basim Trading Bot — تسجيل الدخول" if self.lang == "ar" else "Basim Trading Bot - Login")

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            # lighter cyan theme
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0 y1:0, x2:1 y2:1,
                                  stop:0 #041926, stop:1 #065f73);
                    color: #f3f4f6;
                }
                QLabel { color: #e6eef0; }
                QLineEdit {
                    background: rgba(255,255,255,0.06);
                    border: 1px solid rgba(255,255,255,0.08);
                    padding: 8px;
                    border-radius: 6px;
                    color: #ffffff;
                }
            """)
            self.theme_btn.setText("☀️")
        else:
            self._apply_styles()
            self.theme_btn.setText("🌙")

    def _focus_password(self):
        self.password_input.setFocus()

    def _on_login_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.msg_label.setText("الرجاء إدخال اسم المستخدم وكلمة المرور" if self.lang=="ar" else "Please enter username and password")
            return

        # Call project auth.login (returns dict)
        try:
            result = auth.login(username, password)
        except Exception as e:
            self.msg_label.setText(("فشل الاتصال، حاول مرة أخرى." if self.lang=="ar" else "Login failed; try again."))
            return

        # result expected like: {'status':'success','role':'user'} or {'status':'pending'}
        status = result.get("status")
        role = result.get("role", "user")

        if status == "success":
            # open main window, pass username and role
            self.open_main_window(username, role)
        elif status == "pending":
            self.msg_label.setText("طلبك قيد الموافقة من المطور." if self.lang=="ar" else "Your request is pending developer approval.")
        elif status == "fail":
            # show generic fail
            self.msg_label.setText("اسم المستخدم أو كلمة المرور غير صحيحة." if self.lang=="ar" else "Invalid username or password.")
        else:
            # fallback message
            self.msg_label.setText(str(result))

    def open_main_window(self, username, role="user"):
        # Create MainWindow with username and role, then close login
        self.main_win = MainWindow(username=username, role=role, lang=self.lang)
        self.main_win.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
