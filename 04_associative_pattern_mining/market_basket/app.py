"""Flask UI and recommendation API."""
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .pipeline import mine
from .mining import recommend


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder=str(Path(__file__).parents[1] / "templates"))
    app.config.from_mapping(
        DATA_PATH=str(Path(__file__).parents[1] / "sample_transactions.json"),
        MIN_SUPPORT=float(os.getenv("MIN_SUPPORT", "0.15")),
        MIN_CONFIDENCE=float(os.getenv("MIN_CONFIDENCE", "0.5")),
        MIN_LIFT=float(os.getenv("MIN_LIFT", "1.0")),
    )
    if config:
        app.config.update(config)
    transactions, _, rules = mine(app.config["DATA_PATH"], app.config["MIN_SUPPORT"], app.config["MIN_CONFIDENCE"], app.config["MIN_LIFT"])
    catalog = sorted(set().union(*transactions))

    @app.get("/")
    def index():
        return render_template("index.html", catalog=catalog)

    @app.post("/api/recommend")
    def api_recommend():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            return jsonify(error="JSON body must contain an items list"), 400
        items = payload["items"]
        if not items or not all(isinstance(item, str) and item.strip() for item in items):
            return jsonify(error="items must be a non-empty list of non-blank strings"), 400
        basket = {item.strip().lower() for item in items}
        unknown = sorted(basket - set(catalog))
        if unknown:
            return jsonify(error="unknown items", unknown_items=unknown), 400
        return jsonify(basket=sorted(basket), recommendations=recommend(basket, rules))

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app


app = create_app()
