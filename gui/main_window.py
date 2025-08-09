import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTabWidget, QLabel, QMessageBox, QApplication
)
from core.translation_utils import load_translation
from database.db_manager import check_user_status, is_subscription_valid

class TradingTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🔄 Auto Trading Tab (سيتم تطويره لاحقًا)"))
        self.setLayout(layout)

class ManualTradingTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🖐️ Manual Trading Tab (سيتم تطويره لاحقًا)"))
        self.setLayout(layout)

class BacktestTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📊 Backtest Tab (سيتم تطويره لاحقًا)"))
        self.setLayout(layout)

class ReportsTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📈 Reports Tab (سيتم تطويره لاحقًا)"))
        self.setLayout(layout)

class SettingsTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("⚙️ Settings Tab (سيتم تطويره لاحقًا)"))
        self.setLayout(layout)

class ContactTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📬 Contact Us Tab (سيتم تطويره لاحقًا)"))
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self, username="", role="user", lang="en"):
        super().__init__()
        self.username = username
        self.role = role
        self.lang = lang
        self.trans = load_translation(self.lang)
        self.setWindowTitle(f"{self.trans['login_title']} - {self.username}")
        self.setGeometry(400, 200, 700, 500)
        self.init_ui()

        # التحقق من حالة المستخدم واشتراكه فقط
        if self.role == "user":
            status = check_user_status(self.username)
            if status != "active":
                QMessageBox.critical(self, "خروج", "حسابك غير مفعل من المطور.")
                QApplication.quit()
            elif not is_subscription_valid(self.username):
                QMessageBox.critical(self, "خروج", "اشتراكك منتهي أو غير صالح.")
                QApplication.quit()
            # تم إزالة show_renewal_alert بالكامل

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.btn_theme = QPushButton(self.trans["change_theme"])
        self.btn_theme.clicked.connect(self.change_theme)

        self.btn_lang = QPushButton(self.trans["change_language"])
        self.btn_lang.clicked.connect(self.change_language)

        self.btn_logout = QPushButton(self.trans["logout"])
        self.btn_logout.clicked.connect(self.logout)

        self.tabs = QTabWidget()
        self.tabs.addTab(TradingTab(lang=self.lang), self.trans.get("tab_trading", "Trading"))
        self.tabs.addTab(ManualTradingTab(lang=self.lang), self.trans.get("tab_manual", "Manual"))
        self.tabs.addTab(BacktestTab(lang=self.lang), self.trans.get("tab_backtest", "Backtest"))
        self.tabs.addTab(ReportsTab(lang=self.lang), self.trans.get("tab_reports", "Reports"))
        self.tabs.addTab(SettingsTab(lang=self.lang), self.trans.get("tab_settings", "Settings"))
        self.tabs.addTab(ContactTab(lang=self.lang), self.trans.get("tab_contact", "Contact Us"))

        layout.addWidget(self.tabs)
        layout.addWidget(self.btn_theme)
        layout.addWidget(self.btn_lang)
        layout.addWidget(self.btn_logout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def change_theme(self):
        if self.styleSheet() == "":
            try:
                with open("gui/styles/dark.qss", "r") as f:
                    self.setStyleSheet(f.read())
            except Exception:
                QMessageBox.warning(self, "Theme", "Dark theme file not found!")
        else:
            self.setStyleSheet("")

    def change_language(self):
        self.lang = "ar" if self.lang == "en" else "en"
        self.trans = load_translation(self.lang)
        self.setWindowTitle(f"{self.trans['login_title']} - {self.username}")

    def logout(self):
        QMessageBox.information(self, "خروج", "تم تسجيل الخروج.")
        QApplication.quit()