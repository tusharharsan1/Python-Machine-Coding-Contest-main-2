from typing import List

from sqlalchemy.orm import Session

from models.product import Product
from models.product_group import ProductGroup
from repositories.repository import Repository


class ProductGroupsRepository(Repository[ProductGroup]):
    def __init__(self, session: Session):
        super().__init__(session, ProductGroup)

    def find_by_products_containing(self, product: Product) -> List[ProductGroup]:
        # TODO: Return all the product groups which contain this product.
        #   Hint: for a many-to-many relationship, `.contains(...)` checks if a product is in the list, for example
        #     self.session.query(ProductGroup).filter(ProductGroup.products.contains(product)).all()
        pass
