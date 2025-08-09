import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QGraphicsDropShadowEffect, QFrame, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from core.subscription_manager import record_txid_request, notify_telegram_txid
from gui.main_window import MainWindow

USDT_WALLET_ADDRESS = "TYtsxSRYFsSAEcLFzcnNaqwi7vTwQgHmFn"

class RenewalPromptWindow(QWidget):
    def __init__(self, days_remaining, username, lang="ar", early_discount=True):
        super().__init__()
        self.lang = lang
        self.days_remaining = days_remaining
        self.username = username
        self.early_discount = early_discount
        self.dark_mode = True
        self.setWindowTitle("Basim Trading Bot — تجديد الاشتراك" if lang == "ar" else "Basim Trading Bot - Renewal")
        self.resize(500, 370)
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

        title = QLabel("⚠️")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        glass_layout.addWidget(title)

        # نص التنبيه حسب حالة الخصم
        if self.early_discount:
            message = f"اشتراكك سينتهي خلال {self.days_remaining} أيام. يمكن الإستمتاع بخصم 10% في حالة التجديد المبكر."
        else:
            message = f"انتهى اشتراكك، يمكنك الآن التجديد بنفس السعر (بدون خصم)."

        self.msg_label = QLabel(message)
        self.msg_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setStyleSheet("color: #fbbf24; margin-bottom: 8px;")
        glass_layout.addWidget(self.msg_label)

        wallet_label = QLabel("عنوان محفظة USDT (TRC20):")
        wallet_label.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        glass_layout.addWidget(wallet_label)

        addr_row = QHBoxLayout()
        self.addr_val = QLabel(USDT_WALLET_ADDRESS)
        self.addr_val.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.addr_val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        addr_row.addWidget(self.addr_val)

        btn_copy = QPushButton("نسخ العنوان")
        btn_copy.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_copy.setFixedHeight(28)
        btn_copy.setStyleSheet("background-color: #10b981; color: white;")
        btn_copy.clicked.connect(self.copy_address)
        addr_row.addWidget(btn_copy)
        glass_layout.addLayout(addr_row)

        txid_label = QLabel("أدخل TxID الخاص بعملية الدفع:")
        txid_label.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        glass_layout.addWidget(txid_label)

        self.input_txid = QLineEdit()
        self.input_txid.setPlaceholderText("TxID")
        self.input_txid.setFont(QFont("Segoe UI", 11))
        glass_layout.addWidget(self.input_txid)

        btn_send = QPushButton("إرسال طلب التجديد" if self.lang == "ar" else "Send Renewal Request")
        btn_send.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_send.setFixedHeight(36)
        btn_send.setStyleSheet("background-color: #10b981; color: white;")
        btn_send.clicked.connect(self.on_send_renewal)
        glass_layout.addWidget(btn_send)

        btn_close = QPushButton("إغلاق" if self.lang == "ar" else "Close")
        btn_close.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_close.setFixedHeight(32)
        btn_close.setStyleSheet("background-color: #334155; color: white;")
        btn_close.clicked.connect(self.on_close)
        glass_layout.addWidget(btn_close)

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

    def copy_address(self):
        QApplication.clipboard().setText(USDT_WALLET_ADDRESS)
        QMessageBox.information(self, "تم النسخ", "تم نسخ عنوان المحفظة بنجاح!")

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
                border-radius: 6px;
            }
            QLineEdit {
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                color: #ffffff;
                padding: 8px;
            }
        """)

    def on_send_renewal(self):
        txid = self.input_txid.text().strip()
        if not txid:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال TxID صالح." if self.lang == "ar" else "Please enter a valid TxID.")
            return
        record_txid_request(self.username, txid)
        sent = notify_telegram_txid(self.username, txid)
        if sent:
            QMessageBox.information(self, "تم", "تم إرسال الطلب للمطور بنجاح." if self.lang == "ar" else "Renewal request sent successfully.")
            self.open_main_window()
        else:
            QMessageBox.warning(self, "فشل", "فشل إرسال الطلب للمطور، حاول لاحقًا." if self.lang == "ar" else "Failed to send request, try again later.")

    def on_close(self):
        # عند الإغلاق، افتح MainWindow بدل الإغلاق الكامل
        self.open_main_window()

    def open_main_window(self):
        self.main_win = MainWindow(username=self.username, role='user', lang=self.lang)
        self.main_win.show()
        self.close()

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RenewalPromptWindow(days_remaining=3, username="demo")
    win.show()
    sys.exit(app.exec_())