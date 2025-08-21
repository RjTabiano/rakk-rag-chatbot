from typing import Optional, List, Dict, Any
from app.utils.db_connection import get_db_connection
from langchain.tools import StructuredTool

BASE_PRODUCT_URL = "http://127.0.0.1:8080"

def search_products(keyword: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("Selecting all products from database")
    query = """
        SELECT id, name, description, category, price, stock_quantity, image_path
        FROM products
    """
    if limit:
        query += " LIMIT %s"
        cursor.execute(query, (limit,))
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Attach product links for frontend rendering
    for product in results:
        product["link"] = f"{BASE_PRODUCT_URL}/{product['id']}"

    print(f"Found {len(results)} products")
    return results


search_products_tool = StructuredTool.from_function(
    func=search_products,
    name="search_products",
    description="Searches the product database by keyword and returns product details (name, description, price, stock)."
)