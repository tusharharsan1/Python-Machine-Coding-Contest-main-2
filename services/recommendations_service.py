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

        # TODO Step 1: Look up the product with self.product_repository.find_by_id(product_id).
        #   If there is no such product (you get None), raise ProductNotFoundException("...some message...").

        # TODO Step 2: Find all the ProductGroups that contain this product.
        #   Use: self.product_groups_repository.find_by_products_containing(product)

        # TODO Step 3: Collect the products of all those groups into ONE list.
        #   Every group has a list of products: group.products
        #   Loop over the groups, and loop over group.products inside it, adding every product to a list.

        # TODO Step 4: Remove the duplicates and the product itself.
        #   The same product can be in many groups, but it must appear only once in the answer.
        #   Compare products using their id (product.id), and skip the product whose id is product_id.

        # TODO Step 5: Return the list of recommended products (and delete the line `return None` below).

        return None
