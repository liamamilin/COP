"""
get_product_info — 本地产品目录查询工具。

参数：product_id (string, 必需) — 产品 ID，格式 P001–P005。
返回：包含 name/price/category/in_stock 的字典，或错误字典。

不依赖 LangChain 或外部库。
"""

from __future__ import annotations

import json
from pathlib import Path

_PRODUCTS_PATH = Path(__file__).parent / "products.json"


def _load_products() -> dict:
    with open(_PRODUCTS_PATH, encoding="utf-8") as f:
        return json.load(f)


_PRODUCTS: dict | None = None


def _get_products() -> dict:
    global _PRODUCTS
    if _PRODUCTS is None:
        _PRODUCTS = _load_products()
    return _PRODUCTS


def get_product_info(product_id: str) -> dict:
    """查询产品目录中指定 ID 的产品信息。

    返回产品名称、价格、分类和库存状态。
    product_id 必须是 P001 到 P005 之间的字符串。
    如果产品不存在，返回错误信息。
    """
    if not isinstance(product_id, str):
        return {"error": "Invalid product_id type", "product_id": str(product_id)}

    products = _get_products()

    if product_id not in products:
        return {"error": "Product not found", "product_id": product_id}

    product = products[product_id]
    return {
        "name": product["name"],
        "price": product["price"],
        "category": product["category"],
        "in_stock": product["in_stock"],
    }


def reset_cache() -> None:
    """清除产品缓存，用于测试。"""
    global _PRODUCTS
    _PRODUCTS = None
