from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, urllib.parse

app = Flask(__name__)
CORS(app)  # CORS 설정

# ▶️ 카페24 앱 정보
CLIENT_ID = "dBwJWYGCFlMgnYhZIUekBA"
CLIENT_SECRET = "pt9fuUjdYa5Nf3lasDbLvL"
REDIRECT_URI = "https://delivus-tony.github.io/cafe24-auth-test/callback.html"
SCOPES = "mall.read_product mall.write_product"

# 🔹 1단계: mall_id 받아 인증 URL 생성
@app.route("/install", methods=["POST"])
def install():
    data = request.get_json()
    mall_id = data.get("mall_id")
    if not mall_id:
        return "❌ mall_id 없음", 400

    store_domain = f"{mall_id}.cafe24api.com"
    auth_url = make_auth_url(CLIENT_ID, REDIRECT_URI, store_domain, SCOPES, mall_id)

    return auth_url

def make_auth_url(client_id, redirect_uri, store_domain, scopes, mall_id):
    base = f"https://{store_domain}/api/v2/oauth/authorize"
    
    query = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,  # 쿼리스트링 붙이지 마세요!
        "scope": scopes,
        "state": mall_id  # mall_id는 여기에 넣고 나중에 되돌려 받기
    }
    return f"{base}?{urllib.parse.urlencode(query)}"

# 🔹 2단계: code + mall_id 받아서 access token 요청
@app.route("/token", methods=["POST"])
def get_token():
    data = request.get_json()
    mall_id = data.get("mall_id")
    code = data.get("code")

    if not mall_id or not code:
        return "❌ mall_id 또는 code가 없습니다", 400

    token_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }

    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return {"error": str(e)}, 500

# Render에서 실행용
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
