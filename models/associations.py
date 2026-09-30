from sqlalchemy import Column, ForeignKey, Integer, Table

from models.base_model import Base

# A product group has many products and a product can be in many groups (many-to-many).
# A many-to-many relationship needs a table of its own in between:
# every row of this table says "this product is part of this product group".
product_group_products = Table(
    "product_group_products",
    Base.metadata,
    Column("product_group_id", Integer, ForeignKey("product_groups.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)
