from dtos.generate_recommendations_request_dto import GenerateRecommendationsRequestDto
from dtos.generate_recommendations_response_dto import GenerateRecommendationsResponseDto
from dtos.response_status import ResponseStatus
from services.recommendations_service import RecommendationsService


class RecommendationsController:
    def __init__(self, recommendations_service: RecommendationsService):
        self.recommendations_service = recommendations_service

    def generate_recommendations(self, request_dto: GenerateRecommendationsRequestDto) \
            -> GenerateRecommendationsResponseDto:
        response_dto = GenerateRecommendationsResponseDto()
        try:
            recommendations = self.recommendations_service.get_recommendations(request_dto.product_id)
            response_dto.recommendations = recommendations
            response_dto.response_status = ResponseStatus.SUCCESS
        except Exception:
            # If ANY exception happens (for example ProductNotFoundException), the status is FAILURE
            # and recommendations must stay None.
            response_dto.response_status = ResponseStatus.FAILURE
        return response_dto
