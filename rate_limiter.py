import time
from collections import deque

class RateLimiter:
    def __init__(self, config):
        self.config = config
        self.rate_limit = config.get("rate_limit")
        self.requests = deque()
        
    def check_rate_limit(self):
        """Check if current request is within rate limits"""
        if not self.rate_limit["enabled"]:
            return True
            
        current_time = time.time()
        window_start = current_time - self.rate_limit["time_window"]
        
        # Remove old requests
        while self.requests and self.requests[0] < window_start:
            self.requests.popleft()
            
        # Check if we're under the limit
        if len(self.requests) < self.rate_limit["max_requests"]:
            self.requests.append(current_time)
            return True
            
        return False
        
    def get_remaining_requests(self):
        """Get number of remaining requests in current window"""
        current_time = time.time()
        window_start = current_time - self.rate_limit["time_window"]
        
        # Remove old requests
        while self.requests and self.requests[0] < window_start:
            self.requests.popleft()
            
        return self.rate_limit["max_requests"] - len(self.requests)
