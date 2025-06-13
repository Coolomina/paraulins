import os

from flask import Flask
from flask_cors import CORS

from config import config
from routes.api import api
from routes.web import web


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Determine which config to use
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV") or "default"

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(web)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_ENV", "development") != "production"

    print("Starting Paraulins webapp...")
    print(f"Open your browser to: http://localhost:{port}")
    app.run(debug=debug, host="0.0.0.0", port=port)  # nosec
