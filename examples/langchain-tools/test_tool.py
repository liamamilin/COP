"""get_product_info 工具的单元测试。

覆盖：有效 ID、未知 ID、错误类型、空值、缓存重置。
不依赖 LangChain 或外部服务。
"""

import pytest

from tool import get_product_info, reset_cache


@pytest.fixture(autouse=True)
def _clear_cache():
    reset_cache()
    yield
    reset_cache()


class TestValidProductIds:
    def test_P001_returns_full_info(self):
        result = get_product_info("P001")
        assert result["name"] == "LangChain 入门教程"
        assert result["price"] == 99.00
        assert result["category"] == "教程"
        assert result["in_stock"] is True

    def test_P002_agent_book(self):
        result = get_product_info("P002")
        assert result["name"] == "Agent 开发实战"
        assert result["price"] == 149.00
        assert result["category"] == "教程"
        assert result["in_stock"] is True

    def test_P003_out_of_stock(self):
        result = get_product_info("P003")
        assert result["name"] == "Prompt 工程指南"
        assert result["price"] == 79.00
        assert result["category"] == "电子书"
        assert result["in_stock"] is False

    def test_P004(self):
        result = get_product_info("P004")
        assert result["name"] == "RAG 系统构建"
        assert result["price"] == 129.00

    def test_P005_cheapest_ebook(self):
        result = get_product_info("P005")
        assert result["name"] == "向量数据库对比"
        assert result["price"] == 59.00
        assert result["category"] == "电子书"
        assert result["in_stock"] is True

    def test_all_five_products_queryable(self):
        for pid in ("P001", "P002", "P003", "P004", "P005"):
            result = get_product_info(pid)
            assert "error" not in result
            assert "name" in result
            assert "price" in result


class TestUnknownProductId:
    def test_P999_not_found(self):
        result = get_product_info("P999")
        assert result == {"error": "Product not found", "product_id": "P999"}

    def test_numeric_string_not_found(self):
        result = get_product_info("123")
        assert result == {"error": "Product not found", "product_id": "123"}

    def test_empty_string_not_found(self):
        result = get_product_info("")
        assert result == {"error": "Product not found", "product_id": ""}

    def test_lowercase_p001_not_found(self):
        result = get_product_info("p001")
        assert result == {"error": "Product not found", "product_id": "p001"}

    def test_close_but_wrong_id(self):
        result = get_product_info("P006")
        assert result == {"error": "Product not found", "product_id": "P006"}


class TestInvalidTypes:
    def test_none_returns_error(self):
        result = get_product_info(None)
        assert result["error"] == "Invalid product_id type"

    def test_int_returns_error(self):
        result = get_product_info(123)
        assert result["error"] == "Invalid product_id type"

    def test_float_returns_error(self):
        result = get_product_info(3.14)
        assert result["error"] == "Invalid product_id type"

    def test_list_returns_error(self):
        result = get_product_info(["P001"])
        assert result["error"] == "Invalid product_id type"

    def test_dict_returns_error(self):
        result = get_product_info({"id": "P001"})
        assert result["error"] == "Invalid product_id type"

    def test_bool_returns_error(self):
        result = get_product_info(True)
        assert result["error"] == "Invalid product_id type"


class TestNoUnhandledExceptions:
    def test_all_invalid_inputs_return_dict(self):
        """工具对任何输入都返回字典，不抛出未捕获异常。"""
        inputs = [None, 0, 123, 3.14, [], {}, True, "", "P999", "xyz"]
        for inp in inputs:
            result = get_product_info(inp)
            assert isinstance(result, dict)


class TestReturnValueShape:
    def test_success_has_exactly_four_keys(self):
        result = get_product_info("P001")
        assert set(result.keys()) == {"name", "price", "category", "in_stock"}

    def test_error_has_exactly_two_keys(self):
        result = get_product_info("P999")
        assert set(result.keys()) == {"error", "product_id"}

    def test_type_error_has_exactly_two_keys(self):
        result = get_product_info(None)
        assert set(result.keys()) == {"error", "product_id"}

    def test_price_is_float(self):
        result = get_product_info("P001")
        assert isinstance(result["price"], float)

    def test_in_stock_is_bool(self):
        result = get_product_info("P001")
        assert isinstance(result["in_stock"], bool)
