import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class TxIDWindow(QWidget):
    def __init__(self, username, lang="ar"):
        super().__init__()
        self.username = username
        self.lang = lang
        self.dark_mode = True
        self.setWindowTitle("إدخال TxID" if lang == "ar" else "Enter TxID")
        self.resize(400, 250)
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

        title = QLabel("💳" if self.lang == "ar" else "💳")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(title)

        msg = "أدخل TxID الخاص بعملية الدفع:" if self.lang == "ar" else "Enter your payment TxID:"
        label = QLabel(msg)
        label.setFont(QFont("Segoe UI", 12))
        label.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(label)

        self.input_txid = QLineEdit()
        self.input_txid.setPlaceholderText("TxID")
        self.input_txid.setFont(QFont("Segoe UI", 11))
        glass_layout.addWidget(self.input_txid)

        btn_send = QPushButton("إرسال" if self.lang == "ar" else "Send")
        btn_send.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_send.setFixedHeight(40)
        btn_send.clicked.connect(self.send_txid)
        glass_layout.addWidget(btn_send)

        btn_close = QPushButton("إغلاق" if self.lang == "ar" else "Close")
        btn_close.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_close.setFixedHeight(36)
        btn_close.clicked.connect(self.close)
        glass_layout.addWidget(btn_close)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 130))
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
                    stop:0 rgba(255,255,255,0.08), stop:1 rgba(255,255,255,0.15));
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 12px;
            }
            QPushButton {
                background-color: rgba(16, 185, 129, 0.92);
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(5, 150, 105, 0.97);
            }
            QLineEdit {
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 8px;
                color: #ffffff;
                padding: 8px;
            }
        """)

    def send_txid(self):
        txid = self.input_txid.text().strip()
        if not txid:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال TxID صالح." if self.lang == "ar" else "Please enter a valid TxID.")
            return
        # هنا يمكن ربط الكود لإرسال الطلب للمطور أو حفظه في قاعدة البيانات
        print(f"تم إدخال TxID: {txid} للمستخدم: {self.username}")
        QMessageBox.information(self, "تم", "تم إرسال TxID بنجاح." if self.lang == "ar" else "TxID sent successfully.")
        self.close()

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TxIDWindow(username="demo")
    win.show()
    sys.exit(app.exec_())