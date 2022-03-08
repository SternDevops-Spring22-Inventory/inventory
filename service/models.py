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
condition (int) - New (0), Returned/used (1), or Unknown (2)

"""
import logging
from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Pet.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Condition(Enum):
    """Enumeration of valid Item Conditions"""

    NEW = 0
    USED = 1
    UNKNOWN = 2


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
        db.Enum(condition), nullable=False, server_default=(Condition.UNKNOWN.name)
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
        """Serializes a Pet into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "available": self.available,
            "gender": self.gender.name,  # convert enum to string
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Pet from a dictionary
        Args:
            data (dict): A dictionary containing the Pet data
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
            self.gender = getattr(Gender, data["gender"])  # create enum from string
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid pet: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data " + str(error)
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
        """Returns all of the Pets in the database"""
        logger.info("Processing all Pets")
        return cls.query.all()

    @classmethod
    def find(cls, pet_id: int):
        """Finds a Pet by it's ID

        :param pet_id: the id of the Pet to find
        :type pet_id: int

        :return: an instance with the pet_id, or None if not found
        :rtype: Pet

        """
        logger.info("Processing lookup for id %s ...", pet_id)
        return cls.query.get(pet_id)

    @classmethod
    def find_or_404(cls, pet_id: int):
        """Find a Pet by it's id

        :param pet_id: the id of the Pet to find
        :type pet_id: int

        :return: an instance with the pet_id, or 404_NOT_FOUND if not found
        :rtype: Pet

        """
        logger.info("Processing lookup or 404 for id %s ...", pet_id)
        return cls.query.get_or_404(pet_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Returns all Pets with the given name

        :param name: the name of the Pets you want to match
        :type name: str

        :return: a collection of Pets with that name
        :rtype: list

        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_category(cls, category: str) -> list:
        """Returns all of the Pets in a category

        :param category: the category of the Pets you want to match
        :type category: str

        :return: a collection of Pets in that category
        :rtype: list

        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Returns all Pets by their availability

        :param available: True for pets that are available
        :type available: str

        :return: a collection of Pets that are available
        :rtype: list

        """
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available)

    @classmethod
    def find_by_gender(cls, gender: Gender = Gender.UNKNOWN) -> list:
        """Returns all Pets by their Gender

        :param gender: values are ['MALE', 'FEMALE', 'UNKNOWN']
        :type available: enum

        :return: a collection of Pets that are available
        :rtype: list

        """
        logger.info("Processing gender query for %s ...", gender.name)
        return cls.query.filter(cls.gender == gender)
