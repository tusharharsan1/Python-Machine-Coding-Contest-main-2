# Importing every model here makes sure SQLAlchemy knows about all the tables
# before they are created. Do not remove any line.
from models.base_model import Base, BaseModel
from models.product import Product
from models.product_group import ProductGroup
from models.associations import product_group_products
