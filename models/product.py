from sqlalchemy import Column, Float, String

from models.base_model import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    name = Column(String)
    description = Column(String)
    price = Column(Float)

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name!r})"
