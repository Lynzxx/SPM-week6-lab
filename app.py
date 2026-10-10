from flask import Flask, jsonify, render_template_string, request

from duckfine import DuckFine

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>QuackLoan fine checker</title>
</head>
<body>
  <h1>QuackLoan fine checker</h1>
  <form method="get" action="/">
    <label for="days">Days late</label>
    <input id="days" name="days" type="number" min="0" value="{{ days }}">
    <label>
      <input name="deluxe" type="checkbox" value="1" {% if deluxe %}checked{% endif %}>
      Deluxe duck
    </label>
    <button type="submit">Check fine</button>
  </form>
  {% if error %}
    <p id="error" role="alert">{{ error }}</p>
  {% elif fee is not none %}
    <p id="result">Fine: ${{ "%.2f"|format(fee) }}</p>
  {% endif %}
</body>
</html>
"""


def parse_days(days_param):
    """Return (days, error); exactly one of them is None."""
    try:
        days = int(days_param)
    except ValueError:
        return None, "days must be a whole number"
    if days < 0:
        return None, "days must not be negative"
    return days, None


@app.get("/")
def index():
    days_param = request.args.get("days")
    deluxe = request.args.get("deluxe") == "1"
    fee = error = None
    if days_param is not None:
        days, error = parse_days(days_param)
        if error is None:
            fee = DuckFine("web").charge(days, deluxe=deluxe)
    return render_template_string(
        PAGE, days=days_param or "", deluxe=deluxe, fee=fee, error=error
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/fine")
def fine():
    days, error = parse_days(request.args.get("days", ""))
    if error:
        return jsonify(error=error), 400

    deluxe = request.args.get("deluxe") == "1"
    fee = DuckFine("api").charge(days, deluxe=deluxe)
    return jsonify(days=days, deluxe=deluxe, fee=fee)


if __name__ == "__main__":
    app.run(debug=True)
