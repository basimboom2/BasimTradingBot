import base64

# ضع بياناتك هنا
token = "7963470425:AAGTxK3QAiK-qvSpYoe0suh1Q4ivWoi3rfs"
chat_id = "-1002874958202"

data = f"{token}:{chat_id}"
encoded = base64.b64encode(data.encode()).decode()

with open("core/dev_info.txt", "w") as f:
    f.write(encoded)