from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QLineEdit

class TradingTab(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        layout = QVBoxLayout()

        # اختيار العملة
        pair_layout = QHBoxLayout()
        pair_label = QLabel("Pair:")
        self.pair_combo = QComboBox()
        self.pair_combo.addItems(["BTCUSDT", "ETHUSDT", "BNBUSDT"])  # يمكنك التوسعة لاحقًا
        pair_layout.addWidget(pair_label)
        pair_layout.addWidget(self.pair_combo)

        # اختيار الرافعة المالية
        leverage_layout = QHBoxLayout()
        leverage_label = QLabel("Leverage:")
        self.leverage_input = QLineEdit("10")
        leverage_layout.addWidget(leverage_label)
        leverage_layout.addWidget(self.leverage_input)

        # اختيار الاستراتيجية
        strategy_layout = QHBoxLayout()
        strategy_label = QLabel("Strategy:")
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["EMA Crossover", "RSI", "MACD"])  # يمكنك التوسعة لاحقًا
        strategy_layout.addWidget(strategy_label)
        strategy_layout.addWidget(self.strategy_combo)

        # زر بدء التداول
        self.start_btn = QPushButton("Start Trading")
        # self.start_btn.clicked.connect(self.start_trading)  # سنربطه لاحقًا

        # عرض الصفقات المفتوحة (بسيط كبداية)
        self.open_trades_label = QLabel("Open Trades: (سيتم عرضها هنا)")

        layout.addLayout(pair_layout)
        layout.addLayout(leverage_layout)
        layout.addLayout(strategy_layout)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.open_trades_label)

        self.setLayout(layout)