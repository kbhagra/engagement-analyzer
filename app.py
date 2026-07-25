"""CampaignLens — Flask application entry point (shared file).

Run with:
    python app.py
Then open http://127.0.0.1:5000/results
"""

from flask import Flask

from routes.results_routes import results_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(results_bp)

    # Abraham registers his search blueprint here:
    # from routes.search_routes import search_bp
    # app.register_blueprint(search_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)