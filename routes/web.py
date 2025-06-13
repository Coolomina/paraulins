from flask import Blueprint, render_template
from services.data_service import DataService

web = Blueprint("web", __name__)


def get_data_service():
    """Get DataService instance"""
    return DataService()


@web.route("/")
def index():
    """Main page"""
    data_service = get_data_service()
    children = data_service.get_children()
    return render_template("index.html", children=children)


@web.route("/child/<child_name>")
def child_page(child_name):
    """Child-specific page"""
    data_service = get_data_service()
    child = data_service.get_child(child_name)
    if not child:
        return render_template("error.html", message="Child not found"), 404

    return render_template("child.html", child=child)
