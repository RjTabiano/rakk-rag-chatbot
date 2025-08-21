"""
Lightweight product service without LangChain dependencies.
"""
from typing import Optional, List, Dict, Any
from app.utils.db_connection import get_db_connection

BASE_PRODUCT_URL = "http://127.0.0.1:8080"

def search_products(keyword: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Search products in the database.
    
    Args:
        keyword: Optional search keyword (currently not used in query)
        limit: Maximum number of products to return
        
    Returns:
        List of product dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        print("Selecting all products from database")
        
        query = """
            SELECT id, name, description, category, price, stock_quantity, image_path
            FROM products
        """
        
        # Add limit if specified
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
        
    except Exception as e:
        print(f"Error searching products: {e}")
        return []
