from sqlalchemy.orm import Session

from models.product import Product
from repositories.repository import Repository


class ProductRepository(Repository[Product]):
    def __init__(self, session: Session):
        super().__init__(session, Product)
