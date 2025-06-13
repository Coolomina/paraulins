from flask import Flask
from flask_cors import CORS
from routes.api import api
from routes.web import web
from config import Config


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)

    Config.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(web)

    return app


if __name__ == "__main__":
    app = create_app()
    print("Starting Family Voices webapp...")
    print("Open your browser to: http://localhost:5001")
    app.run(debug=True, host="0.0.0.0", port=5001)
