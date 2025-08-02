# CRUD operations package
from .wealth_product_crud import (
    get_product_by_yindeng_code,
    get_products,
    create_product,
    update_product,
    upsert_product_by_yindeng_code,
    get_all_products,
    get_products_by_query_date,
    query_dynamic
)

from .investment_crud import (
    create_asset,
    get_asset,
    get_asset_by_code,
    get_assets,
    update_asset,
    delete_asset,
    create_transaction,
    get_transaction,
    get_transactions,
    get_transactions_by_product,
    get_transactions_by_asset,
    get_transactions_by_date_range,
    update_transaction,
    delete_transaction
)

__all__ = [
    # Wealth product CRUD operations
    "get_product_by_yindeng_code",
    "get_products",
    "create_product",
    "update_product",
    "upsert_product_by_yindeng_code",
    "get_all_products",
    "get_products_by_query_date",
    "query_dynamic",
    
    # Investment CRUD operations
    "create_asset",
    "get_asset",
    "get_asset_by_code",
    "get_assets",
    "update_asset",
    "delete_asset",
    "create_transaction",
    "get_transaction",
    "get_transactions",
    "get_transactions_by_product",
    "get_transactions_by_asset",
    "get_transactions_by_date_range",
    "update_transaction",
    "delete_transaction",
]