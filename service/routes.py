"""
Inventory Service

Paths:
------
POST /inventory - creates a new Item record in the database
"""

from flask import jsonify, request, url_for, make_response, abort
from werkzeug.exceptions import NotFound
from service.models import Items
from . import status  # HTTP Status Codes
from . import app  # Import Flask application

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Inventory Demo REST API Service",
            version="1.0",
            paths=url_for("list_items", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_item():
    """
    Creates an Item
    This endpoint will create an Item based the data in the body that is posted
    """
    app.logger.info("Request to create an item")
    check_content_type("application/json")
    item = Items()
    item.deserialize(request.get_json())
    item.create()
    message = item.serialize()
    location_url = url_for("get_items", item_id=item.id, _external=True)

    app.logger.info("Item with ID [%s] created.", item.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )

