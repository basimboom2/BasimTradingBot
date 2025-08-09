import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class PendingApprovalWindow(QWidget):
    def __init__(self, lang="ar"):
        super().__init__()
        self.lang = lang
        self.dark_mode = True
        self.setWindowTitle("Basim Trading Bot — انتظار الموافقة" if lang == "ar" else "Basim Trading Bot - Pending Approval")
        self.resize(500, 300)
        self._build_ui()
        self._apply_styles()
        self.center()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        glass_frame = QFrame()
        glass_frame.setObjectName("glassFrame")
        glass_layout = QVBoxLayout(glass_frame)
        glass_layout.setContentsMargins(30, 30, 30, 30)
        glass_layout.setSpacing(15)

        title = QLabel("⏳")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(title)

        message = "⏳ مرحباً بك.. طلبك قيد المراجعة من قِبل المطور.. برجاء الإنتظار قليلا وإعادة المحاولة بعد دقائق حتى يتم إعتماد إشتراكك الجديد" if self.lang == "ar" else "⏳ Your request is under review by the developer. Please wait or try again in a few minutes."
        self.msg_label = QLabel(message)
        self.msg_label.setFont(QFont("Segoe UI", 12))
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(self.msg_label)

        close_btn = QPushButton("إغلاق" if self.lang == "ar" else "Close")
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.close)
        glass_layout.addWidget(close_btn)

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
            QPushButton {
                background-color: rgba(239, 68, 68, 0.9);
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(220, 38, 38, 0.95);
            }
        """)

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PendingApprovalWindow()
    win.show()
    sys.exit(app.exec_())