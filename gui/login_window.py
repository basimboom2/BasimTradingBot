import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QFont, QColor
from core import auth
from gui.main_window import MainWindow
from gui.renewal_prompt_window import RenewalPromptWindow
from gui.pending_approval_window import PendingApprovalWindow
from database.db_manager import get_subscription_dates, is_subscription_valid

def get_days_remaining(username):
    _, end_str = get_subscription_dates(username)
    if not end_str:
        return None
    try:
        end_date = datetime.fromisoformat(end_str)
        delta = end_date - datetime.now()
        days_left = delta.days + (1 if delta.seconds > 0 else 0)
        return days_left
    except Exception:
        return None

class LoginWindow(QWidget):
    def __init__(self, lang="ar"):
        super().__init__()
        self.lang = lang
        self.dark_mode = True
        self.setWindowTitle("Basim Trading Bot — تسجيل الدخول" if lang == "ar" else "Basim Trading Bot - Login")
        self.resize(500, 400)
        self._build_ui()
        self._apply_styles()
        self.center()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        glass_frame = QFrame()
        glass_frame.setObjectName("glassFrame")
        glass_frame.setMinimumWidth(360)
        glass_frame.setMaximumWidth(380)
        glass_layout = QVBoxLayout(glass_frame)
        glass_layout.setContentsMargins(30, 30, 30, 30)
        glass_layout.setSpacing(12)

        self.title = QLabel("Basim Trading Bot")
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(self.title)

        self.subtitle = QLabel("الرجاء تسجيل الدخول للمتابعة" if self.lang == "ar" else "Please sign in to continue")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setFont(QFont("Segoe UI", 10))
        glass_layout.addWidget(self.subtitle)

        user_row = QHBoxLayout()
        user_icon = QLabel("👤")
        user_icon.setFont(QFont("Segoe UI", 14))
        user_row.addWidget(user_icon)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم" if self.lang == "ar" else "Username")
        user_row.addWidget(self.username_input)
        glass_layout.addLayout(user_row)

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
        glass_layout.addLayout(pass_row)

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
        glass_layout.addLayout(row_btns)

        self.login_btn = QPushButton("دخول" if self.lang == "ar" else "Login")
        self.login_btn.setFixedHeight(42)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_btn.clicked.connect(self._on_login_clicked)
        glass_layout.addWidget(self.login_btn)

        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(self.msg_label)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 150))
        glass_frame.setGraphicsEffect(shadow)

        wrapper = QVBoxLayout()
        wrapper.addStretch()
        wrapper.addWidget(glass_frame, alignment=Qt.AlignCenter)
        wrapper.addStretch()
        main_layout.addLayout(wrapper)

        self.username_input.returnPressed.connect(self._focus_password)
        self.password_input.returnPressed.connect(self._on_login_clicked)

    def _apply_styles(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0b1220, stop:0.5 #14202b, stop:1 #23303d);
                    color: #f3f4f6;
                }
                #glassFrame {
                    background: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0,
                        stop:0 rgba(255,255,255,0.03), stop:0.6 rgba(255,255,255,0.07), stop:1 rgba(255,255,255,0.12));
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 15px;
                    padding: 12px;
                }
                QLineEdit {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    padding: 8px;
                    border-radius: 8px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(72,187,120,0.98), stop:1 rgba(16,185,129,0.95));
                    color: white;
                    border-radius: 8px;
                    padding: 6px 12px;
                }
                QPushButton:hover { opacity: 0.95; }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 #eaf2ff, stop:0.5 #f6f9fe, stop:1 #ffffff);
                    color: #102233;
                }
                #glassFrame {
                    background: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0,
                        stop:0 rgba(255,255,255,0.6), stop:1 rgba(255,255,255,0.9));
                    border: 1px solid rgba(0, 0, 0, 0.05);
                    border-radius: 15px;
                    padding: 12px;
                }
                QLineEdit {
                    background: rgba(255, 255, 255, 0.95);
                    border: 1px solid #dbe7f5;
                    padding: 8px;
                    border-radius: 8px;
                    color: #102233;
                }
                QPushButton {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(59,130,246,0.95), stop:1 rgba(96,165,250,0.95));
                    color: white;
                    border-radius: 8px;
                    padding: 6px 12px;
                }
                QPushButton:hover { opacity: 0.95; }
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
            status = auth.get_login_status(username, password)
            print("Login status for user:", username, "=", status)
        except Exception as e:
            self.msg_label.setText("خطأ في الاتصال" if self.lang=="ar" else "Connection error")
            return

        days_remaining = get_days_remaining(username)

        # شاشة انتظار الموافقة للمستخدم الجديد (غير موجود بقاعدة البيانات)
        if status == 'waiting_approval':
            self.msg_label.setText("⏳ طلبك قيد المراجعة من قِبل المطور.. برجاء الإنتظار قليلا أو إعادة المحاولة بعد دقائق")
            self.open_pending_approval(username)
        # إذا كان الاشتراك منتهي أو غير صالح
        elif status == 'active':
            if not is_subscription_valid(username):
                self.msg_label.setText("انتهت مدة اشتراكك. يمكنك التجديد الآن.")
                self.open_renewal_prompt(username, days_remaining=0, early_discount=False)
            elif days_remaining is not None and days_remaining <= 5:
                self.open_renewal_prompt(username, days_remaining, early_discount=True)
            else:
                self.open_main_window(username, role='user')
        elif status == 'superuser':
            self.open_main_window(username, role='superuser')
        elif status == 'expired' or (days_remaining is not None and days_remaining <= 0):
            self.msg_label.setText("انتهت مدة اشتراكك. يمكنك التجديد الآن.")
            self.open_renewal_prompt(username, days_remaining=0, early_discount=False)
        else:
            self.msg_label.setText("بيانات الدخول غير صحيحة" if self.lang=="ar" else "Invalid credentials")

    def open_pending_approval(self, username):
        self.pending_win = PendingApprovalWindow(lang=self.lang)
        self.pending_win.show()
        self.hide()
        loop = QEventLoop()
        self.pending_win.destroyed.connect(loop.quit)
        loop.exec_()
        # بعد الإغلاق يرجع المستخدم لشاشة الدخول فقط
        self.show()

    def open_renewal_prompt(self, username, days_remaining, early_discount=True):
        self.renew_win = RenewalPromptWindow(days_remaining=days_remaining, username=username, lang=self.lang, early_discount=early_discount)
        self.renew_win.show()
        self.hide()
        loop = QEventLoop()
        self.renew_win.destroyed.connect(loop.quit)
        loop.exec_()
        # بعد إغلاق نافذة التجديد، MainWindow يفتح تلقائي من نافذة التجديد نفسها

    def open_main_window(self, username, role="user"):
        self.main_win = MainWindow(username=username, role=role, lang=self.lang)
        self.main_win.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())