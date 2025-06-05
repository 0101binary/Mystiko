import os
import hashlib
import time
from pathlib import Path
from datetime import datetime

class PayloadManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.output_dir = Path(config.get("output_dir"))
        self.temp_dir = Path(config.get("temp_dir"))
        self.payload_history = []
        
    def generate_payload_name(self, base_name):
        """Generate unique payload name with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}"
        
    def save_payload(self, payload_data, name):
        """Save payload with metadata"""
        payload_name = self.generate_payload_name(name)
        output_path = self.output_dir / payload_name
        
        # Save payload
        with open(output_path, 'wb') as f:
            f.write(payload_data)
            
        # Generate hash
        payload_hash = hashlib.sha256(payload_data).hexdigest()
        
        # Record metadata
        metadata = {
            'name': payload_name,
            'hash': payload_hash,
            'timestamp': datetime.now().isoformat(),
            'size': len(payload_data)
        }
        
        self.payload_history.append(metadata)
        self.logger.info(f"Payload saved: {payload_name}")
        
        return output_path, metadata
        
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        for file in self.temp_dir.glob("*"):
            try:
                file.unlink()
            except Exception as e:
                self.logger.error(f"Error cleaning up {file}: {e}")
                
    def get_payload_history(self):
        """Get payload generation history"""
        return self.payload_history
