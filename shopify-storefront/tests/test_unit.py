# -*- coding: utf-8 -*-
"""
Unit tests for Shopify Storefront integration.
Tests validation logic and error handling without live API calls.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shopify_storefront import (
    validate_shop_url,
    require_input,
    require_one_of,
    parse_graphql_response,
    extract_user_errors,
    error_response,
    success_response,
)


class TestValidateShopUrl:
    """Tests for shop URL validation and SSRF protection."""

    def test_valid_myshopify_url(self):
        assert validate_shop_url("my-store.myshopify.com") == "my-store.myshopify.com"

    def test_strips_https(self):
        assert validate_shop_url("https://my-store.myshopify.com") == "my-store.myshopify.com"

    def test_strips_http(self):
        assert validate_shop_url("http://my-store.myshopify.com") == "my-store.myshopify.com"

    def test_strips_trailing_slash(self):
        assert validate_shop_url("my-store.myshopify.com/") == "my-store.myshopify.com"

    def test_empty_url_raises(self):
        with pytest.raises(ValueError, match="Missing required credential: shop_url"):
            validate_shop_url("")

    def test_none_url_raises(self):
        with pytest.raises(ValueError, match="Missing required credential: shop_url"):
            validate_shop_url(None)

    def test_non_myshopify_domain_raises(self):
        with pytest.raises(ValueError, match="must be a \\*.myshopify.com domain"):
            validate_shop_url("evil-site.com")

    def test_path_injection_raises(self):
        with pytest.raises(ValueError, match="contains forbidden characters"):
            validate_shop_url("my-store.myshopify.com/admin")

    def test_userinfo_injection_raises(self):
        with pytest.raises(ValueError, match="contains forbidden characters"):
            validate_shop_url("attacker@my-store.myshopify.com")

    def test_port_injection_raises(self):
        with pytest.raises(ValueError, match="contains forbidden characters"):
            validate_shop_url("my-store.myshopify.com:8080")


class TestRequireInput:
    """Tests for required input validation."""

    def test_valid_input(self):
        assert require_input({"cart_id": "abc123"}, "cart_id") == "abc123"

    def test_missing_key_raises(self):
        with pytest.raises(ValueError, match="Missing required parameter: cart_id"):
            require_input({}, "cart_id")

    def test_none_value_raises(self):
        with pytest.raises(ValueError, match="Missing required parameter: cart_id"):
            require_input({"cart_id": None}, "cart_id")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Missing required parameter: cart_id"):
            require_input({"cart_id": ""}, "cart_id")

    def test_zero_is_valid(self):
        assert require_input({"count": 0}, "count") == 0

    def test_false_is_valid(self):
        assert require_input({"flag": False}, "flag") == False


class TestRequireOneOf:
    """Tests for at-least-one-of validation."""

    def test_first_key_present(self):
        require_one_of({"handle": "my-product"}, "handle", "product_id")

    def test_second_key_present(self):
        require_one_of({"product_id": "gid://shopify/Product/123"}, "handle", "product_id")

    def test_both_present(self):
        require_one_of({"handle": "my-product", "product_id": "123"}, "handle", "product_id")

    def test_none_present_raises(self):
        with pytest.raises(ValueError, match="At least one of these parameters is required"):
            require_one_of({}, "handle", "product_id")

    def test_empty_values_raises(self):
        with pytest.raises(ValueError, match="At least one of these parameters is required"):
            require_one_of({"handle": "", "product_id": None}, "handle", "product_id")


class TestParseGraphqlResponse:
    """Tests for GraphQL response parsing."""

    def test_success_response(self):
        response = {"data": {"products": []}}
        data, errors = parse_graphql_response(response)
        assert data == {"products": []}
        assert errors == []

    def test_single_error(self):
        response = {"errors": [{"message": "Not found"}]}
        data, errors = parse_graphql_response(response)
        assert data is None
        assert errors == ["Not found"]

    def test_multiple_errors(self):
        response = {"errors": [{"message": "Error 1"}, {"message": "Error 2"}]}
        data, errors = parse_graphql_response(response)
        assert errors == ["Error 1", "Error 2"]

    def test_error_with_code(self):
        response = {"errors": [{"message": "Access denied", "extensions": {"code": "FORBIDDEN"}}]}
        data, errors = parse_graphql_response(response)
        assert errors == ["FORBIDDEN: Access denied"]

    def test_invalid_response_type(self):
        data, errors = parse_graphql_response("not a dict")
        assert data is None
        assert errors == ["Invalid response type from API"]

    def test_partial_data_with_errors(self):
        response = {"data": {"product": None}, "errors": [{"message": "Partial failure"}]}
        data, errors = parse_graphql_response(response)
        assert data == {"product": None}
        assert errors == ["Partial failure"]


class TestExtractUserErrors:
    """Tests for mutation user error extraction."""

    def test_no_errors(self):
        data = {"cartCreate": {"cart": {"id": "123"}, "userErrors": []}}
        errors = extract_user_errors(data, "cartCreate")
        assert errors == []

    def test_single_error(self):
        data = {"cartCreate": {"userErrors": [{"message": "Invalid line item"}]}}
        errors = extract_user_errors(data, "cartCreate")
        assert errors == ["Invalid line item"]

    def test_multiple_errors(self):
        data = {"cartCreate": {"userErrors": [{"message": "Error 1"}, {"message": "Error 2"}]}}
        errors = extract_user_errors(data, "cartCreate")
        assert errors == ["Error 1", "Error 2"]

    def test_customer_user_errors(self):
        data = {"customerCreate": {"customerUserErrors": [{"message": "Email taken"}]}}
        errors = extract_user_errors(data, "customerCreate", "customerUserErrors")
        assert errors == ["Email taken"]

    def test_none_data(self):
        errors = extract_user_errors(None, "cartCreate")
        assert errors == []

    def test_missing_mutation_key(self):
        data = {"otherKey": {}}
        errors = extract_user_errors(data, "cartCreate")
        assert errors == []


class TestResponseHelpers:
    """Tests for response helper functions."""

    def test_success_response(self):
        result = success_response(products=[], count=0)
        assert result.data == {"success": True, "products": [], "count": 0}

    def test_error_response_string(self):
        result = error_response("Something went wrong", products=None)
        assert result.data == {"success": False, "message": "Something went wrong", "products": None}

    def test_error_response_list(self):
        result = error_response(["Error 1", "Error 2"])
        assert result.data == {"success": False, "message": "Error 1; Error 2"}

    def test_error_response_empty_list(self):
        result = error_response([])
        assert result.data == {"success": False, "message": "Unknown error"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
