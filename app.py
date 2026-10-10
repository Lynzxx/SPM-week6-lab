from flask import Flask, jsonify, request

from duckfine import DuckFine

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/fine")
def fine():
    days_param = request.args.get("days", "")
    try:
        days = int(days_param)
    except ValueError:
        return jsonify(error="days must be a whole number"), 400
    if days < 0:
        return jsonify(error="days must not be negative"), 400

    deluxe = request.args.get("deluxe") == "1"
    fee = DuckFine("api").charge(days, deluxe=deluxe)
    return jsonify(days=days, deluxe=deluxe, fee=fee)


if __name__ == "__main__":
    app.run(debug=True)
