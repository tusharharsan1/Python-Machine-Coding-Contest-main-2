from models.base_model import BaseModel

# TODO: Complete this model.
#
# A ProductGroup is a group of products which are frequently bought together.
# One group has many products and one product can be part of many groups (many-to-many).
# The table in between is already written for you in models/associations.py.
#
# Steps (add the missing imports at the top of the file):
#   from sqlalchemy.orm import relationship
#   from models.associations import product_group_products
#
# 1. Add the attribute
#        products = relationship("Product", secondary=product_group_products)
#    `secondary=` tells SQLAlchemy which in-between table connects the two sides.
#    After this, `group.products` gives you the list of Product objects of the group.
#
# Hint: models/associations.py shows the table that `secondary` points to.


class ProductGroup(BaseModel):
    __tablename__ = "product_groups"  # already given, keep it

    def __repr__(self):
        return f"ProductGroup(id={self.id})"
