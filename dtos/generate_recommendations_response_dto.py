from typing import List, Optional

from dtos.response_status import ResponseStatus
from models.product import Product


class GenerateRecommendationsResponseDto:
    """The response: the recommended products and whether it worked."""

    def __init__(self):
        self.recommendations: Optional[List[Product]] = None
        self.response_status: Optional[ResponseStatus] = None
