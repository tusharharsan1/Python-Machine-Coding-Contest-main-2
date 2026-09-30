class GenerateRecommendationsRequestDto:
    """The request: the id of the product which the user is going to buy."""

    def __init__(self, product_id: int):
        self.product_id = product_id
