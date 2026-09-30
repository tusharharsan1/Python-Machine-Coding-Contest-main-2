"""A small demo that shows how everything is wired together. Run it with:  python main.py

The wiring has 4 steps: 1) create a session  2) create repositories  3) create the service
4) create the controller. Nothing to change in this file.
"""
from controllers.recommendations_controller import RecommendationsController
from db.database import create_session
from dtos.generate_recommendations_request_dto import GenerateRecommendationsRequestDto
from models.product import Product
from models.product_group import ProductGroup
from repositories.product_groups_repository import ProductGroupsRepository
from repositories.product_repository import ProductRepository
from services.recommendations_service import RecommendationsService


def main():
    session = create_session()

    product_repository = ProductRepository(session)
    product_groups_repository = ProductGroupsRepository(session)
    service = RecommendationsService(product_repository, product_groups_repository)
    controller = RecommendationsController(service)

    # some data to play with
    phone = product_repository.save(Product(name="Mobile phone", description="5G phone", price=30000.0))
    cover = product_repository.save(Product(name="Cover", description="Back cover", price=300.0))
    glass = product_repository.save(Product(name="Tempered glass", description="Screen guard", price=200.0))
    insurance = product_repository.save(Product(name="Insurance", description="1 year cover", price=1500.0))

    product_groups_repository.save(ProductGroup(products=[phone, cover]))
    product_groups_repository.save(ProductGroup(products=[phone, glass]))
    product_groups_repository.save(ProductGroup(products=[phone, insurance]))
    product_groups_repository.save(ProductGroup(products=[phone, glass, cover]))

    response = controller.generate_recommendations(GenerateRecommendationsRequestDto(product_id=phone.id))

    print("Status:", response.response_status)
    if response.recommendations is not None:
        print("Recommended:", [product.name for product in response.recommendations])


if __name__ == "__main__":
    main()
