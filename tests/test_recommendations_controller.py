import unittest

from controllers.recommendations_controller import RecommendationsController
from db.database import create_session
from dtos.generate_recommendations_request_dto import GenerateRecommendationsRequestDto
from dtos.response_status import ResponseStatus
from exceptions.product_not_found_exception import ProductNotFoundException
from models.associations import product_group_products
from models.product import Product
from models.product_group import ProductGroup
from repositories.product_groups_repository import ProductGroupsRepository
from repositories.product_repository import ProductRepository
from services.recommendations_service import RecommendationsService


class RecommendationsTestBase(unittest.TestCase):
    """Common setup used by the test classes below.

    Before EVERY test we build a brand new, empty database and fill it with these products:
        phone (id 1), cover (id 2), glass (id 3), insurance (id 4), charger (id 5), laptop (id 6), bag (id 7)
    and these product groups:
        [phone, cover]   [phone, glass]   [phone, insurance]   [phone, glass, cover]   [laptop, bag]
    (so `charger` is in no group at all)
    """

    def setUp(self):
        self.session = create_session()
        self.product_repository = ProductRepository(self.session)
        self.product_groups_repository = ProductGroupsRepository(self.session)
        self.service = RecommendationsService(self.product_repository, self.product_groups_repository)
        self.controller = RecommendationsController(self.service)

        self.phone = self._add_product("Mobile phone", 30000.0)
        self.cover = self._add_product("Cover", 300.0)
        self.glass = self._add_product("Tempered glass", 200.0)
        self.insurance = self._add_product("Insurance", 1500.0)
        self.charger = self._add_product("Charger", 999.0)
        self.laptop = self._add_product("Laptop", 60000.0)
        self.bag = self._add_product("Laptop bag", 800.0)

        self._add_group(self.phone, self.cover)
        self._add_group(self.phone, self.glass)
        self._add_group(self.phone, self.insurance)
        self._add_group(self.phone, self.glass, self.cover)
        self._add_group(self.laptop, self.bag)

    def tearDown(self):
        engine = self.session.get_bind()
        self.session.close()
        engine.dispose()

    # ---------- helpers ----------
    def _add_product(self, name, price):
        return self.product_repository.save(Product(name=name, description=name + " description", price=price))

    def _add_group(self, *products):
        return self.product_groups_repository.save(ProductGroup(products=list(products)))

    def _recommend(self, product):
        """Calls the controller for this product (or for this plain id)."""
        product_id = product.id if isinstance(product, Product) else product
        return self.controller.generate_recommendations(GenerateRecommendationsRequestDto(product_id=product_id))

    def _ids(self, products):
        return sorted(product.id for product in products)

    def _count(self, model):
        self.session.expire_all()
        return self.session.query(model).count()

    def assert_recommends(self, product, expected_products):
        """The call must succeed and return exactly these products (any order, no repeats)."""
        response = self._recommend(product)
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertIsNotNone(response.recommendations)
        self.assertEqual(self._ids(expected_products), self._ids(response.recommendations))

    def assert_failure(self, response):
        self.assertEqual(ResponseStatus.FAILURE, response.response_status)
        self.assertIsNone(response.recommendations)


# ======================================================================================
# 1. The model and the repository query (each can earn marks on its own)
# ======================================================================================
class ModelAndRepositoryTest(RecommendationsTestBase):

    def test_product_group_keeps_its_products(self):
        group = self._add_group(self.laptop, self.bag, self.charger)
        self.session.expire_all()
        loaded = self.product_groups_repository.find_by_id(group.id)
        self.assertEqual(self._ids([self.laptop, self.bag, self.charger]), self._ids(loaded.products))

    def test_products_of_a_group_are_product_objects(self):
        group = self._add_group(self.laptop, self.bag)
        self.session.expire_all()
        loaded = self.product_groups_repository.find_by_id(group.id)
        for product in loaded.products:
            self.assertIsInstance(product, Product)
        self.assertEqual({"Laptop", "Laptop bag"}, {product.name for product in loaded.products})

    def test_an_empty_product_group_can_be_saved(self):
        group = self._add_group()
        self.session.expire_all()
        self.assertEqual([], self.product_groups_repository.find_by_id(group.id).products)

    def test_the_same_product_can_be_part_of_many_groups(self):
        # the phone is already in 4 groups from setUp
        self.session.expire_all()
        groups_with_phone = [g for g in self.product_groups_repository.find_all()
                             if self.phone.id in [p.id for p in g.products]]
        self.assertEqual(4, len(groups_with_phone))

    def test_many_to_many_rows_are_stored_in_the_in_between_table(self):
        self.session.expire_all()
        rows = self.session.execute(product_group_products.select()).fetchall()
        # 2 + 2 + 2 + 3 + 2 members in the groups created in setUp
        self.assertEqual(11, len(rows))

    def test_find_by_products_containing_returns_every_group_of_the_product(self):
        groups = self.product_groups_repository.find_by_products_containing(self.phone)
        self.assertEqual(4, len(groups))

    def test_find_by_products_containing_returns_only_groups_with_that_product(self):
        groups = self.product_groups_repository.find_by_products_containing(self.glass)
        self.assertEqual(2, len(groups))
        for group in groups:
            self.assertIn(self.glass.id, [product.id for product in group.products])

    def test_find_by_products_containing_for_a_product_of_another_group(self):
        groups = self.product_groups_repository.find_by_products_containing(self.bag)
        self.assertEqual(1, len(groups))
        self.assertEqual(self._ids([self.laptop, self.bag]), self._ids(groups[0].products))

    def test_find_by_products_containing_returns_empty_list_when_product_is_in_no_group(self):
        self.assertEqual([], self.product_groups_repository.find_by_products_containing(self.charger))

    def test_find_by_products_containing_does_not_repeat_a_group(self):
        groups = self.product_groups_repository.find_by_products_containing(self.cover)
        self.assertEqual(len(groups), len({group.id for group in groups}))
        self.assertEqual(2, len(groups))


# ======================================================================================
# 2. The controller alone: a fake service lets us check ONLY what the controller does
# ======================================================================================
class FakeRecommendationsService:
    """Pretends to be RecommendationsService. Remembers how it was called."""

    def __init__(self, products_to_return=None, error_to_raise=None):
        self.products_to_return = products_to_return
        self.error_to_raise = error_to_raise
        self.calls = []

    def get_recommendations(self, product_id):
        self.calls.append(product_id)
        if self.error_to_raise is not None:
            raise self.error_to_raise
        return self.products_to_return


class ControllerOnlyTest(unittest.TestCase):

    def test_success_returns_the_list_from_the_service_and_success_status(self):
        products = [Product(name="a"), Product(name="b")]
        controller = RecommendationsController(FakeRecommendationsService(products_to_return=products))
        response = controller.generate_recommendations(GenerateRecommendationsRequestDto(product_id=5))
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertIs(products, response.recommendations)

    def test_an_empty_list_is_still_a_success_and_stays_an_empty_list(self):
        controller = RecommendationsController(FakeRecommendationsService(products_to_return=[]))
        response = controller.generate_recommendations(GenerateRecommendationsRequestDto(product_id=5))
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual([], response.recommendations)

    def test_controller_passes_the_product_id_of_the_request(self):
        service = FakeRecommendationsService(products_to_return=[])
        RecommendationsController(service).generate_recommendations(GenerateRecommendationsRequestDto(product_id=42))
        self.assertEqual([42], service.calls)

    def test_controller_passes_a_different_product_id_too(self):
        service = FakeRecommendationsService(products_to_return=[])
        RecommendationsController(service).generate_recommendations(GenerateRecommendationsRequestDto(product_id=7))
        self.assertEqual([7], service.calls)

    def test_any_exception_gives_failure_and_no_recommendations(self):
        for error in (ProductNotFoundException("x"), RuntimeError("something else"), ValueError("v")):
            with self.subTest(error=type(error).__name__):
                controller = RecommendationsController(FakeRecommendationsService(error_to_raise=error))
                response = controller.generate_recommendations(GenerateRecommendationsRequestDto(product_id=1))
                self.assertEqual(ResponseStatus.FAILURE, response.response_status)
                self.assertIsNone(response.recommendations)

    def test_the_controller_does_not_raise_when_the_service_fails(self):
        controller = RecommendationsController(FakeRecommendationsService(error_to_raise=KeyError("boom")))
        try:
            response = controller.generate_recommendations(GenerateRecommendationsRequestDto(product_id=1))
        except Exception as error:
            self.fail(f"The controller must catch the exception, but it raised {error!r}")
        self.assertEqual(ResponseStatus.FAILURE, response.response_status)


# ======================================================================================
# 3. The whole flow through the controller
# ======================================================================================
class RecommendationsControllerTest(RecommendationsTestBase):

    def test_example_of_the_problem_statement(self):
        self.assert_recommends(self.phone, [self.cover, self.glass, self.insurance])

    def test_recommendations_are_returned_as_a_list_of_products(self):
        response = self._recommend(self.phone)
        self.assertIsInstance(response.recommendations, list)
        for product in response.recommendations:
            self.assertIsInstance(product, Product)

    def test_the_product_itself_is_never_recommended(self):
        response = self._recommend(self.phone)
        self.assertNotIn(self.phone.id, [product.id for product in response.recommendations])

    def test_no_product_is_recommended_twice(self):
        # the glass is in 2 groups with the phone and the cover is in 2 groups with the phone
        response = self._recommend(self.phone)
        ids = [product.id for product in response.recommendations]
        self.assertEqual(3, len(ids))
        self.assertEqual(len(ids), len(set(ids)))

    def test_products_of_unrelated_groups_are_not_recommended(self):
        response = self._recommend(self.phone)
        ids = [product.id for product in response.recommendations]
        self.assertNotIn(self.laptop.id, ids)
        self.assertNotIn(self.bag.id, ids)
        self.assertNotIn(self.charger.id, ids)

    def test_recommendations_come_from_every_group_of_the_product(self):
        # cover, glass and insurance come from three different groups, insurance from a group of its own
        response = self._recommend(self.phone)
        self.assertIn(self.insurance.id, [product.id for product in response.recommendations])

    def test_recommendations_for_a_product_that_is_bought_with_the_phone(self):
        # the cover is in [phone, cover] and [phone, glass, cover]
        self.assert_recommends(self.cover, [self.phone, self.glass])

    def test_recommendations_for_the_glass(self):
        self.assert_recommends(self.glass, [self.phone, self.cover])

    def test_recommendations_for_a_product_with_a_single_partner(self):
        self.assert_recommends(self.insurance, [self.phone])

    def test_recommendations_for_a_different_group_of_products(self):
        self.assert_recommends(self.laptop, [self.bag])
        self.assert_recommends(self.bag, [self.laptop])

    def test_product_in_no_group_gets_an_empty_list_and_success(self):
        response = self._recommend(self.charger)
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual([], response.recommendations)

    def test_product_which_is_alone_in_its_group_gets_an_empty_list(self):
        loner = self._add_product("Loner", 1.0)
        self._add_group(loner)
        response = self._recommend(loner)
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual([], response.recommendations)

    def test_a_big_group_recommends_everything_else_in_it(self):
        extras = [self._add_product(f"Extra {i}", 10.0 + i) for i in range(6)]
        self._add_group(self.charger, *extras)
        self.assert_recommends(self.charger, extras)

    def test_overlapping_groups_are_merged_without_repeats(self):
        a = self._add_product("A", 1.0)
        b = self._add_product("B", 2.0)
        c = self._add_product("C", 3.0)
        d = self._add_product("D", 4.0)
        self._add_group(a, b, c)
        self._add_group(a, b, d)
        self._add_group(a, c, d)
        self.assert_recommends(a, [b, c, d])

    def test_products_with_identical_details_but_different_ids_are_both_recommended(self):
        twin_one = self.product_repository.save(Product(name="USB cable", description="1 metre", price=99.0))
        twin_two = self.product_repository.save(Product(name="USB cable", description="1 metre", price=99.0))
        self._add_group(self.charger, twin_one)
        self._add_group(self.charger, twin_two)
        self.assert_recommends(self.charger, [twin_one, twin_two])

    def test_recommended_products_keep_their_details(self):
        response = self._recommend(self.insurance)
        product = response.recommendations[0]
        self.assertEqual("Mobile phone", product.name)
        self.assertEqual(30000.0, product.price)

    def test_result_depends_on_the_product_asked_for_not_on_a_fixed_id(self):
        self.assertNotEqual(self._ids(self._recommend(self.phone).recommendations),
                            self._ids(self._recommend(self.laptop).recommendations))

    def test_asking_twice_gives_the_same_answer(self):
        first = self._ids(self._recommend(self.phone).recommendations)
        second = self._ids(self._recommend(self.phone).recommendations)
        self.assertEqual(first, second)

    def test_recommending_does_not_change_the_database(self):
        products_before, groups_before = self._count(Product), self._count(ProductGroup)
        self._recommend(self.phone)
        self._recommend(999)
        self.assertEqual(products_before, self._count(Product))
        self.assertEqual(groups_before, self._count(ProductGroup))
        self.assertEqual(4, len(self.product_groups_repository.find_by_products_containing(self.phone)))

    # ---------- failures ----------
    def test_unknown_product_fails(self):
        self.assert_failure(self._recommend(999))

    def test_product_id_zero_fails(self):
        self.assert_failure(self._recommend(0))

    def test_negative_product_id_fails(self):
        self.assert_failure(self._recommend(-1))

    def test_id_just_after_the_last_product_fails(self):
        self.assert_failure(self._recommend(self.bag.id + 1))

    def test_a_failure_can_be_followed_by_a_success(self):
        self.assert_failure(self._recommend(999))
        self.assert_recommends(self.phone, [self.cover, self.glass, self.insurance])

    def test_a_success_can_be_followed_by_a_failure(self):
        self.assert_recommends(self.phone, [self.cover, self.glass, self.insurance])
        self.assert_failure(self._recommend(999))


# ======================================================================================
# 4. The service: the exception which is raised
# ======================================================================================
class RecommendationsServiceTest(RecommendationsTestBase):

    def test_unknown_product_raises_product_not_found(self):
        with self.assertRaises(ProductNotFoundException):
            self.service.get_recommendations(999)

    def test_zero_and_negative_ids_raise_product_not_found(self):
        for product_id in (0, -5):
            with self.subTest(product_id=product_id):
                with self.assertRaises(ProductNotFoundException):
                    self.service.get_recommendations(product_id)

    def test_the_exception_message_is_not_empty(self):
        with self.assertRaises(ProductNotFoundException) as context:
            self.service.get_recommendations(999)
        self.assertTrue(str(context.exception).strip())

    def test_known_product_returns_a_list_of_products(self):
        products = self.service.get_recommendations(self.phone.id)
        self.assertIsInstance(products, list)
        self.assertEqual(self._ids([self.cover, self.glass, self.insurance]), self._ids(products))

    def test_known_product_in_no_group_returns_an_empty_list_and_does_not_raise(self):
        self.assertEqual([], self.service.get_recommendations(self.charger.id))

    def test_the_service_returns_no_duplicates_and_not_the_product_itself(self):
        products = self.service.get_recommendations(self.cover.id)
        ids = [product.id for product in products]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(self.cover.id, ids)


if __name__ == "__main__":
    unittest.main()
