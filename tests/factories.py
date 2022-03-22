"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Items, Condition


class ItemFactory(factory.Factory):
    """Creates fake items that you don't have to account for"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Items

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=["blue shirt", "black pants", "white socks", "brown shorts"])
    category = FuzzyChoice(choices=["shirt", "socks", "pants", "shorts"])
    available = FuzzyChoice(choices=[True, False])
    condition = FuzzyChoice(choices=[Condition.NEW, Condition.USED])