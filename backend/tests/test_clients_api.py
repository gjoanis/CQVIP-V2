def test_create_and_list_client(client):
    payload = {"name": "Acme Pharma", "industry": "Biotech"}
    created = client.post("/clients", json=payload).json()
    assert created["name"] == "Acme Pharma"

    listed = client.get("/clients").json()
    assert any(c["id"] == created["id"] for c in listed)
