# ===================================================
# api_example.py - APIからのデータ取得サンプル
# Week 1 / 指令2
# ===================================================
print("✅ api_example.py が実行されました")

import requests

def get_weather(latitude: float, longitude: float) -> dict:
    """
    Open-Meteo APIから天気情報を取得する。

    Args:
        latitude:  緯度（例: 35.6762）
        longitude: 経度（例: 139.6503）

    Returns:
        天気データの辞書
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status() # ステータスコードが4xx/5xxならエラー
    return response.json()

# ─── 実行例 ───
if __name__ == "__main__":
    data = get_weather(35.6762, 139.6503)        # 東京
    weather = data["current_weather"]

    print(f"🌡️  気温: {weather['temperature']}°C")
    print(f"💨  風速: {weather['windspeed']} km/h")
    print(f"🧭  風向: {weather['winddirection']}°")