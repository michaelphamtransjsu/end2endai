from market_basket.app import create_app


def test_interface_and_health():
    client = create_app({"TESTING": True}).test_client()
    assert client.get("/health").get_json() == {"status": "ok"}
    assert b"Basket Companion" in client.get("/").data


def test_recommendation_endpoint():
    client = create_app({"TESTING": True}).test_client()
    response = client.post("/api/recommend", json={"items": ["chips"]})
    assert response.status_code == 200
    assert {item["item"] for item in response.get_json()["recommendations"]} >= {"salsa"}


def test_recommendation_rejects_unknown_and_malformed_items():
    client = create_app({"TESTING": True}).test_client()
    assert client.post("/api/recommend", json={"items": ["dragonfruit"]}).status_code == 400
    assert client.post("/api/recommend", json={"items": []}).status_code == 400
