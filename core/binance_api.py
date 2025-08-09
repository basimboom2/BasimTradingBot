import json
import os
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

CONFIG_PATH = "config/config.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

config = load_config()

BASE_URL = "https://testnet.binancefuture.com" if config["use_testnet"] else "https://fapi.binance.com"

client = Client(config["api_key"], config["api_secret"])
client.API_URL = BASE_URL

def get_price(symbol):
    try:
        ticker = client.futures_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"Error getting price: {e}")
        return None

def get_balance(asset='USDT'):
    try:
        balances = client.futures_account_balance()
        for entry in balances:
            if entry['asset'] == asset:
                return float(entry['balance'])
        return 0.0
    except Exception as e:
        print(f"Error getting balance: {e}")
        return None

def get_position(symbol):
    try:
        positions = client.futures_position_information(symbol=symbol)
        for pos in positions:
            if float(pos["positionAmt"]) != 0:
                return pos
        return None
    except Exception as e:
        print(f"Error getting position: {e}")
        return None

def place_order(symbol, side, quantity, entry_type="MARKET", price=None, stop_loss=None, take_profits=[]):
    try:
        order_params = {
            'symbol': symbol,
            'side': SIDE_BUY if side == "BUY" else SIDE_SELL,
            'type': ORDER_TYPE_MARKET if entry_type == "MARKET" else ORDER_TYPE_LIMIT,
            'quantity': quantity
        }

        if entry_type == "LIMIT":
            order_params.update({
                'price': str(price),
                'timeInForce': TIME_IN_FORCE_GTC
            })

        main_order = client.futures_create_order(**order_params)

        sl_orders = []
        tp_orders = []

        if stop_loss:
            sl_type = ORDER_TYPE_STOP_MARKET
            sl_side = SIDE_SELL if side == "BUY" else SIDE_BUY
            sl_params = {
                "symbol": symbol,
                "side": sl_side,
                "type": sl_type,
                "stopPrice": str(stop_loss),
                "closePosition": True,
                "timeInForce": TIME_IN_FORCE_GTC
            }
            sl_orders.append(client.futures_create_order(**sl_params))

        for tp in take_profits:
            tp_price = tp.get("price")
            tp_qty = tp.get("quantity", quantity)
            tp_type = ORDER_TYPE_LIMIT
            tp_side = SIDE_SELL if side == "BUY" else SIDE_BUY
            tp_params = {
                "symbol": symbol,
                "side": tp_side,
                "type": tp_type,
                "price": str(tp_price),
                "quantity": tp_qty,
                "timeInForce": TIME_IN_FORCE_GTC,
                "reduceOnly": True
            }
            tp_orders.append(client.futures_create_order(**tp_params))

        return {
            "main": main_order,
            "sl": sl_orders,
            "tp": tp_orders
        }

    except BinanceAPIException as e:
        print(f"Binance error: {e.message}")
        return None
    except Exception as e:
        print(f"Order placement failed: {e}")
        return None

def place_market_order(symbol, side, quantity):
    """
    تنفيذ أمر سوقي (ماركت) سريع
    """
    return place_order(symbol, side, quantity, entry_type="MARKET")

def place_limit_order(symbol, side, quantity, price, stop=False):
    """
    تنفيذ أمر محدد (ليمت). إذا stop=True يعتبر أمر إيقاف خسارة.
    """
    entry_type = "LIMIT"
    return place_order(symbol, side, quantity, entry_type=entry_type, price=price)

def place_trailing_stop_order(symbol, side, quantity, callback_rate=1.0, activation_price=None):
    """
    تنفيذ أمر Trailing Stop على Binance
    """
    try:
        params = {
            'symbol': symbol,
            'side': SIDE_SELL if side == "SELL" else SIDE_BUY,
            'type': ORDER_TYPE_TRAILING_STOP_MARKET,
            'quantity': quantity,
            'callbackRate': callback_rate,
            'reduceOnly': True
        }

        if activation_price:
            params['activationPrice'] = str(activation_price)

        return client.futures_create_order(**params)

    except BinanceAPIException as e:
        print(f"Binance trailing stop error: {e.message}")
        return None
    except Exception as e:
        print(f"Trailing Stop order failed: {e}")
        return None

def cancel_order(symbol, order_id):
    try:
        return client.futures_cancel_order(symbol=symbol, orderId=order_id)
    except Exception as e:
        print(f"Cancel failed: {e}")
        return None

def get_order_status(symbol, order_id):
    try:
        return client.futures_get_order(symbol=symbol, orderId=order_id)
    except Exception as e:
        print(f"Status fetch failed: {e}")
        return None

def get_klines(symbol, interval, limit=100):
    """تحميل بيانات الشموع من Binance"""
    try:
        return client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    except Exception as e:
        print(f"Error fetching klines: {e}")
        return []