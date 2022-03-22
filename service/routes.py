"""
Inventory Service

Paths:
------
POST /inventory - creates a new Item record in the database
DELETE /inventory/{id} - deletes an Item record in the database
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
# RETRIEVE AN INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_items(item_id):
    """
    Retrieve a single Item
    This endpoint will return a Item based on it's id
    """
    app.logger.info("Request for item with id: %s", item_id)
    item = Items.find(item_id)
    if not item:
        raise NotFound("Item with id '{}' was not found.".format(item_id))

    app.logger.info("Returning item: %s", item.name)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["PUT"])
def update_items(item_id):
    """
    Update an Inventory Item
    This endpoint will update an Inventory Item based the body that is posted
    """
    app.logger.info("Request to update item with id: %s", item_id)
    check_content_type("application/json")
    item = Items.find(item_id)
    if not item:
        raise NotFound("Item with id '{}' was not found.".format(item_id))
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    app.logger.info("Item with ID [%s] updated.", item.id)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE AN EXISTING INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    Delete a Item
    This endpoint will delete a Item based the id specified in the path
    """
    app.logger.info("Request to delete item with id: %s", item_id)
    item = Items.find(item_id)
    if item:
        item.delete()

    app.logger.info("Item with ID [%s] delete complete.", item_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


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