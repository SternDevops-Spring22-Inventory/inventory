"""
Inventory Service

Paths:
------
GET /inventory - Returns a list all of the Items
GET /inventory/{id} - Returns the Item with a given id number
POST /inventory - creates a new Item record in the database
PUT /inventory/{id} - updates a Item record in the database
DELETE /inventory/{id} - deletes a Item record in the database
PUT /inventory/{id}/disable
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
    """Base URL for our service"""
    return app.send_static_file("index.html")    

######################################################################
# LIST ALL ITEMS
######################################################################
@app.route("/inventory", methods=["GET"])
def list_items():
    """Returns all of the Items"""
    app.logger.info("Request for item list")
    items = []
    category = request.args.get("category")
    name = request.args.get("name")
    if category:
        items = Items.find_by_category(category)
    elif name:
        items = Items.find_by_name(name)
    else:
        items = Items.all()

    results = [item.serialize() for item in items]
    app.logger.info("Returning %d items", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


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
# Disabling an Item
######################################################################
@app.route("/inventory/<item_id>/disable", methods=["PUT"])
def disable_item(item_id):
    """Disabling an Item makes it unavailable"""
    item = Items.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")
    item.quantity = 0
    item.update()
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)    


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