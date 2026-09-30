from sqlalchemy.orm import relationship

from models.associations import product_group_products
from models.base_model import BaseModel


class ProductGroup(BaseModel):
    """A group of products which are frequently bought together."""
    __tablename__ = "product_groups"

    # One group has many products and one product can be part of many groups (many-to-many).
    # `secondary` is the in-between table (see models/associations.py).
    products = relationship("Product", secondary=product_group_products)

    def __repr__(self):
        return f"ProductGroup(id={self.id})"
