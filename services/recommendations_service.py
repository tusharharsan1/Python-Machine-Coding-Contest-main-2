from typing import List

from exceptions.product_not_found_exception import ProductNotFoundException
from models.product import Product
from repositories.product_groups_repository import ProductGroupsRepository
from repositories.product_repository import ProductRepository


class RecommendationsService:
    """Holds the business logic of finding the products which are frequently bought together.

    The repositories are already handed to you in the constructor, use them to talk to the database.
    """

    def __init__(self, product_repository: ProductRepository,
                 product_groups_repository: ProductGroupsRepository):
        self.product_repository = product_repository
        self.product_groups_repository = product_groups_repository

    def get_recommendations(self, product_id: int) -> List[Product]:
        """Returns the products which are frequently bought together with the given product.

        Raises:
            ProductNotFoundException: if there is no product with this id.
        """

        # Step 1: find the product, it must exist
        product = self.product_repository.find_by_id(product_id)
        if product is None:
            raise ProductNotFoundException(f"Product with id {product_id} not found")

        # Step 2: find all the groups which contain this product
        product_groups = self.product_groups_repository.find_by_products_containing(product)

        # Step 3 and 4: collect the products of all the groups into ONE list,
        # skipping the product itself and the products we have already added
        recommendations = []
        added_ids = set()  # ids of the products already in `recommendations`
        for group in product_groups:
            for other_product in group.products:
                if other_product.id == product_id:
                    continue  # never recommend the product which the user is already buying
                if other_product.id in added_ids:
                    continue  # already recommended through another group
                added_ids.add(other_product.id)
                recommendations.append(other_product)

        # Step 5: return the recommended products
        return recommendations
