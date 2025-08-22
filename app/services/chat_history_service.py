from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from decimal import Decimal
from app.utils.db_connection import get_db_connection

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal objects."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class ChatHistoryService:
    def __init__(self, max_history_length: int = 5):
        self.max_history_length = max_history_length
    
    def save_conversation(
        self, 
        session_id: str, 
        user_message: str, 
        bot_response: str, 
        product_context: Optional[List[Dict]] = None,
        product_links: Optional[List[str]] = None
    ) -> None:
        """Save a conversation turn to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Convert lists to JSON strings for storage, handling Decimal objects
            product_context_json = json.dumps(product_context, cls=DecimalEncoder) if product_context else None
            product_links_json = json.dumps(product_links, cls=DecimalEncoder) if product_links else None
            
            query = """
                INSERT INTO chat_history 
                (session_id, user_message, bot_response, product_context, product_links, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                session_id,
                user_message,
                bot_response,
                product_context_json,
                product_links_json,
                datetime.now()
            ))
            
            conn.commit()
            
            self._cleanup_old_conversations(session_id, cursor, conn)
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving conversation: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = """
                SELECT user_message, bot_response, product_context, product_links, timestamp
                FROM chat_history 
                WHERE session_id = %s 
                ORDER BY timestamp ASC
                LIMIT %s
            """
            
            cursor.execute(query, (session_id, self.max_history_length))
            results = cursor.fetchall()
            
            for result in results:
                if result['product_context']:
                    result['product_context'] = json.loads(result['product_context'])
                if result['product_links']:
                    result['product_links'] = json.loads(result['product_links'])
            
            return results
            
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_formatted_history_context(self, session_id: str) -> str:
        """Get conversation history formatted as context for the LLM."""
        history = self.get_conversation_history(session_id)
        
        if not history:
            return ""
        
        context_parts = []
        for entry in history:
            context_parts.append(f"User: {entry['user_message']}")
            context_parts.append(f"Assistant: {entry['bot_response']}")
        
        return "\n".join(context_parts)
    
    def clear_session_history(self, session_id: str) -> None:
        """Clear all conversation history for a session."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = "DELETE FROM chat_history WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            conn.commit()
            print(f"Cleared chat history for session: {session_id}")
            
        except Exception as e:
            conn.rollback()
            print(f"Error clearing session history: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def _cleanup_old_conversations(self, session_id: str, cursor, conn) -> None:
        """Keep only the last N conversations for a session."""
        try:
            # Get count of conversations for this session
            count_query = "SELECT COUNT(*) as count FROM chat_history WHERE session_id = %s"
            cursor.execute(count_query, (session_id,))
            count = cursor.fetchone()[0]
            
            if count > self.max_history_length:
                delete_query = """
                    DELETE FROM chat_history 
                    WHERE session_id = %s 
                    AND id NOT IN (
                        SELECT id FROM (
                            SELECT id FROM chat_history 
                            WHERE session_id = %s 
                            ORDER BY timestamp DESC 
                            LIMIT %s
                        ) as recent
                    )
                """
                cursor.execute(delete_query, (session_id, session_id, self.max_history_length))
                conn.commit()
                
        except Exception as e:
            print(f"Error cleaning up old conversations: {e}")

chat_history_service = ChatHistoryService()
