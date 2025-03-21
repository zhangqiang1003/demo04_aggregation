from core.http.async_app import app

# asyncio.run(app.run(host="127.0.0.1", port=30133, debug=True))
app.run(host="127.0.0.1", port=18081, debug=True)
