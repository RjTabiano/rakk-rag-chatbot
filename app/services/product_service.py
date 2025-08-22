from typing import Optional, List, Dict, Any
from app.utils.db_connection import get_db_connection
from langchain.tools import StructuredTool
from app.core.config import APP_URL

BASE_PRODUCT_URL = f"{APP_URL}/product_info"

def search_products(keyword: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT id, name, description, category, price, stock_quantity, image_path
        FROM products
    """
    params = []
    
    if keyword:
        # Split keyword
        words = keyword.lower().split()
        if words:
            word_conditions = []
            for word in words:
                word_pattern = f"%{word}%"
                word_conditions.append("(name LIKE %s OR description LIKE %s OR category LIKE %s)")
                params.extend([word_pattern, word_pattern, word_pattern])
            
            # Join all word conditions with OR to find products matching any of the words
            query += f" WHERE {' OR '.join(word_conditions)}"
            print(f"Searching products with keywords: {words}")
        else:
            print("Empty keyword provided, selecting all products")
    else:
        print("Selecting all products from database")
    
    if limit:
        query += " LIMIT %s"
        params.append(limit)
    
    cursor.execute(query, params)
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
    description="Searches the product database by keyword. Searches across name, description, and category fields. Keywords are split into individual words for flexible matching (e.g., 'gaming mouse' will find products containing 'gaming' OR 'mouse'). Use specific product types as keywords (e.g., 'mouse', 'keyboard', 'headset'). Returns matching product details."
)