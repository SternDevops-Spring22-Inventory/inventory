"""
Models for Inventory Demo Service

All of the models are stored in this module

Models
------
Items - Items sold or returned to the store

Attributes:
-----------
name (string) - the name of the item
category (string) - the category the item belongs to (i.e., shirt, shorts)
available (boolean) - True for items that haven't been sold
condition (boolean) - New (0) or Returned/used (1)

"""
import logging
from enum import Enum
from xmlrpc.client import Boolean
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Items.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Condition(Enum):
    """Enumeration of valid Item Conditions"""

    NEW = 0
    USED = 1


class Items(db.Model):
    """
    Class that represents a Item

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    category = db.Column(db.String(63), nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=False)
    condition = db.Column(
        db.Enum(Condition), nullable=False, default=(Condition.NEW)
    )

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return "<Item %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates an Item in the database
        """
        logger.info("Creating %s", self.name)
        # id must be none to generate next primary key
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Item in the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes an Item from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serializes a Item into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "available": self.available,
            "condition": self.condition.name,  # convert enum to string
        }

    def deserialize(self, data: dict):
        """
        Deserializes an Item from a dictionary
        Args:
            data (dict): A dictionary containing the Item data
        """
        try:
            self.name = data["name"]
            self.category = data["category"]
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [available]: "
                    + str(type(data["available"]))
                )
            self.condition = getattr(Condition, data["condition"])  # create enum from string
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid item: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid item: body of request contained bad or no data " + str(error)
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """Returns all of the Items in the database"""
        logger.info("Processing all Items")
        return cls.query.all()

    @classmethod
    def find(cls, pet_id: int):
        """Finds an Item by it's ID

        :param item_id: the id of the Item to find
        :type item_id: int

        :return: an instance with the item_id, or None if not found
        :rtype: Item

        """
        logger.info("Processing lookup for id %s ...", pet_id)
        return cls.query.get(pet_id)

