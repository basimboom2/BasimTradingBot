from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QGroupBox, QFormLayout
)

class ManualTradingTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()

        # --- اختيار العملة والرافعة ---
        pair_layout = QHBoxLayout()
        pair_label = QLabel("Pair:")
        self.pair_combo = QComboBox()
        self.pair_combo.addItems(["BTCUSDT", "ETHUSDT", "BNBUSDT"])
        pair_layout.addWidget(pair_label)
        pair_layout.addWidget(self.pair_combo)

        leverage_layout = QHBoxLayout()
        leverage_label = QLabel("Leverage:")
        self.leverage_input = QLineEdit("10")
        leverage_layout.addWidget(leverage_label)
        leverage_layout.addWidget(self.leverage_input)

        # --- إدخال حجم الصفقة والسعر ---
        trade_group = QGroupBox("Manual Trade Entry")
        trade_form = QFormLayout()
        self.position_size_input = QLineEdit()
        self.entry_price_input = QLineEdit()
        self.stop_loss_input = QLineEdit()
        self.take_profit_input = QLineEdit()
        trade_form.addRow("Position Size (USDT):", self.position_size_input)
        trade_form.addRow("Entry Price:", self.entry_price_input)
        trade_form.addRow("Stop Loss:", self.stop_loss_input)
        trade_form.addRow("Take Profit:", self.take_profit_input)
        trade_group.setLayout(trade_form)

        # --- أزرار فتح/إغلاق الصفقات ---
        self.buy_btn = QPushButton("Buy (Long)")
        self.sell_btn = QPushButton("Sell (Short)")
        self.close_btn = QPushButton("Close Position")
        # يمكنك ربطهم بدوال التنفيذ لاحقًا

        # --- عرض الصفقات المفتوحة ---
        self.open_trades_label = QLabel("Open Trades: (سيتم عرضها هنا)")

        # --- تجميع كل العناصر ---
        layout.addLayout(pair_layout)
        layout.addLayout(leverage_layout)
        layout.addWidget(trade_group)
        layout.addWidget(self.buy_btn)
        layout.addWidget(self.sell_btn)
        layout.addWidget(self.close_btn)
        layout.addWidget(self.open_trades_label)

        self.setLayout(layout)