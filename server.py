from flask import Flask, request, jsonify
import json
import time

app = Flask(__name__)
DATA_FILE = "paddle_log.json"

paddle_position = 0
last_logged = -1

# RESET LOG INFO
@app.route("/reset", methods=["GET"])
def reset_log():
    open(DATA_FILE, "w").close()
    return "Log cleared!"


# GET CURRENT PADDLE POS -
@app.route("/get", methods=["GET"])
def get_pos():
    return {"paddle": paddle_position}


# ESP32 SENDS PADDLE MOVEMENT
@app.route("/update", methods=["GET"])
def update():
    global paddle_position, last_logged

    new_value = int(request.args.get("paddle", "0"))
    try:
        paddle_position = int(request.args.get("paddle", "0"))
    except:
        paddle_position = 0

    #  log changes in paddle position
    if new_value != last_logged:
        last_logged = new_value
        with open(DATA_FILE, "a") as f:
            f.write(json.dumps({
                "type": "paddle",
                "time": time.time(),
                "paddle": new_value
            }) + "\n")

    return f"Paddle received: {paddle_position}"


# SEND FINAL SCORE SUMMARY
@app.route("/gameover", methods=["POST"])
def gameover():
    data = request.json

    with open(DATA_FILE, "a") as f:
        f.write(json.dumps({
            "type": "game_summary",
            "timestamp": time.time(),
            "player_score": data.get("player_score"),
            "ai_score": data.get("ai_score"),
            "player_hits": data.get("player_hits"),
            "ai_hits": data.get("ai_hits"),
            "game_length": data.get("game_length"),
            "winner": data.get("winner")
        }) + "\n")

    return "Game summary saved!"


# HTML LOG PAGE -
@app.route("/log", methods=["GET"])
def log():
    try:
        with open(DATA_FILE) as f:
            lines = f.readlines()

        data = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except:
                continue
    except FileNotFoundError:
        data = []

    html = "<html><head><title>Paddle Log</title></head><body>"
    html += "<h2>Paddle Log</h2>"

    # PADDLE MOVEMENTS TABLE
    html += "<h3>Paddle Movements</h3>"
    html += "<table border='1' style='border-collapse: collapse;'>"
    html += "<tr><th>Time</th><th>Paddle Position</th></tr>"

    for entry in data:
        if entry.get("type") == "paddle":
            t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry["time"]))
            html += f"<tr><td>{t}</td><td>{entry['paddle']}</td></tr>"

    html += "</table>"

    # GAME STATS TABLE
    html += "<h3>Game Summaries</h3>"
    html += "<table border='1' style='border-collapse: collapse;'>"
    html += "<tr><th>Time</th><th>Winner</th><th>Player Score</th><th>AI Score</th><th>Player Hits</th><th>AI Hits</th><th>Length (sec)</th></tr>"

    for entry in data:
        if entry.get("type") == "game_summary":
            t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry["timestamp"]))
            html += f"<tr><td>{t}</td><td>{entry['winner']}</td><td>{entry['player_score']}</td><td>{entry['ai_score']}</td><td>{entry['player_hits']}</td><td>{entry['ai_hits']}</td><td>{entry['game_length']}</td></tr>"

    html += "</table>"
    html += "</body></html>"
    return html

# RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# Access: http://172.20.10.2:5000/log
