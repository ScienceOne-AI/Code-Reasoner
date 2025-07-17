import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class DBLogger:
    def __init__(self, db_path: str = "logs/model_calls.db"):
        """Initialize the database logger."""
        self.db_path = db_path
        self._ensure_db_directory()
        self._create_table()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _create_table(self):
        """Create the calls table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_calls (
                    id TEXT PRIMARY KEY,
                    call_type TEXT NOT NULL,
                    input_prompt TEXT NOT NULL,
                    input_images TEXT,
                    reasoning_content TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT
                )
            """)
            conn.commit()
    
    def log_call(self, 
                 call_type: str, 
                 input_prompt: str, 
                 input_images: Optional[list] = None,
                 reasoning_content: str = "",
                 content: str = "",
                 model_name: str = None) -> str:
        """
        Log a model call to the database.
        
        Args:
            call_type: Either 'generate' or 'generate_with_image'
            input_prompt: The input prompt text
            input_images: List of image paths (for generate_with_image calls)
            reasoning_content: The reasoning content from the response
            content: The content from the response
            model_name: The name of the model used
        
        Returns:
            The unique ID assigned to this call
        """
        call_id = str(uuid.uuid4())
        
        # Convert input_images to JSON string if provided
        input_images_json = json.dumps(input_images) if input_images else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO model_calls 
                (id, call_type, input_prompt, input_images, reasoning_content, content, model_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                call_id,
                call_type,
                input_prompt,
                input_images_json,
                reasoning_content,
                content,
                model_name
            ))
            conn.commit()
        
        return call_id
    
    def get_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific call by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM model_calls WHERE id = ?
            """, (call_id,))
            row = cursor.fetchone()
            
            if row:
                result = dict(row)
                # Parse input_images back to list if it exists
                if result['input_images']:
                    result['input_images'] = json.loads(result['input_images'])
                return result
            return None
    
    def get_recent_calls(self, limit: int = 10) -> list:
        """Get the most recent calls."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM model_calls 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result['input_images']:
                    result['input_images'] = json.loads(result['input_images'])
                results.append(result)
            
            return results 