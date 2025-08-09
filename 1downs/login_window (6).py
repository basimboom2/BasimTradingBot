
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect, QFrame, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from gui.pending_approval_window import PendingApprovalWindow
from gui.renewal_prompt_window import RenewalPromptWindow
from core import auth
from database.db_manager import get_days_remaining

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basim Trading Bot — تسجيل الدخول")
        self.resize(500, 400)
        self._build_ui()
        self._apply_styles()
        self.center()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        glass_frame = QFrame()
        glass_frame.setObjectName("glassFrame")
        glass_layout = QVBoxLayout(glass_frame)
        glass_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Basim Trading Bot")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.returnPressed.connect(self.focus_password)
        glass_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_login_clicked)
        glass_layout.addWidget(self.password_input)

        login_btn = QPushButton("دخول")
        login_btn.clicked.connect(self._on_login_clicked)
        glass_layout.addWidget(login_btn)

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

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #334155);
                color: #f3f4f6;
            }
            #glassFrame {
                background: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0,
                    stop:0 rgba(255,255,255,0.05), stop:1 rgba(255,255,255,0.15));
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 15px;
            }
            QLineEdit, QPushButton {
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton {
                background-color: rgba(16, 185, 129, 0.9);
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(5, 150, 105, 0.95);
            }
        """)

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

    def focus_password(self):
        self.password_input.setFocus()

    def _on_login_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال اسم المستخدم وكلمة المرور")
            return

        status = auth.login(username, password)
        
        if status == "pending":
            self.pending_window = PendingApprovalWindow()
            self.pending_window.show()
            self.close()
            return

        if status == "active":
            days = get_days_remaining(username)
            if days is not None and 0 < days <= 5:
                self.renew_window = RenewalPromptWindow(days_remaining=days)
                self.renew_window.show()
                self.close()
                return

            QMessageBox.information(self, "تم الدخول", f"مرحبًا {username}!")
            self.close()
        else:
            QMessageBox.critical(self, "خطأ", "فشل تسجيل الدخول")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
