# Implement recommend frequently bought products functionality for an e-commerce platform

## Problem Statement

You are building an e-commerce platform. As a part of this system, you need to expose a functionality using which we can recommend users to buy products which are frequently bought together. For example, if a user is buying a mobile phone, then we can recommend the user to buy a mobile cover and a screen guard along with the mobile phone.

## Requirements

Our data science team has figured out frequently bought items using state of the art machine learning algorithms. They have provided us with this data in a table called as `product_groups` represented by ProductGroup model. Each row in this table represents a group of products which are frequently bought together.
Now our task is to use this data and implement a functionality using which we can recommend users to buy products which are frequently bought together.
* The request will contain the product id which the user is going to buy.
* Using this query the product groups table to find out list of distinct products that the user can buy along with the product which the user is going to buy.
* Return the list of products which the user can buy along with the given product. The product which the user is buying must not be part of this list, and no product should appear twice. The order of the products does not matter.
* If there is no product with the given id, the functionality should fail.
* Eg. If the user is buying a mobile phone, and we have the following product groups: [mobile phone, cover], [mobile phone, tempered glass], [mobile phone, insurance], [mobile phone, tempered glass, cover], then we should return the following products: [cover, tempered glass, insurance].

## Instructions (Expected Time: 25 - 30 minutes)

Follow these steps to complete the assignment:

### Step 1: Complete the Model (`models/` package)
- `base_model.py`, `product.py` and `associations.py` are already complete.
- Complete `product_group.py`:
  - Add the `products` relationship (a product group has many products and a product can be in many groups).

### Step 2: Complete the Repository (`repositories/` package)
- `Repository`, `ProductRepository` and the skeleton of `ProductGroupsRepository` are already provided.
- In `ProductGroupsRepository`, complete the method `find_by_products_containing(product)` which returns all the product groups containing the given product.

### Step 3: Implement the Service Logic (`services/recommendations_service.py`)
- The class skeleton is already provided with the repositories.
- Implement `get_recommendations(product_id)` following the `TODO` steps in the file:
  1. Fetch the product by `product_id`. If not found, raise `ProductNotFoundException`.
  2. Find all product groups containing this product using `find_by_products_containing(product)`.
  3. Collect the products of all these groups into a single list.
  4. Remove duplicates and the product itself.
  5. Return the list of recommended products.

### Step 4: Wire the Controller (`controllers/recommendations_controller.py`)
- Implement `generate_recommendations(request_dto)`:
  - Call `recommendations_service.get_recommendations(...)`.
  - Set `response_dto.recommendations` and `ResponseStatus.SUCCESS`.
  - Catch any `Exception`, set `ResponseStatus.FAILURE`, and return.
