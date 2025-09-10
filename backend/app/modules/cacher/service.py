import time
from fastapi import Request

class CacherService:
    def __init__(self):
        self.lastmod = int(time.time())
        self.excluded = False
        self.modified = False

    # Eligibility check (like PHP eligible())
    def is_eligible(self, request: Request) -> bool:
        if self.excluded:
            return False
        if request.method != "GET":
            return False
        return True

    def get_lastmod(self) -> int:
        return self.lastmod

    def update_lastmod(self):
        self.lastmod = int(time.time())
        self.modified = True

    # ETag generation
    def generate_etag(self, request: Request) -> str:
        # Simple example; in PHP it used visitor + route
        return f'W/"{self.lastmod}"'

    # ETag validation
    def validate_etag(self, request: Request) -> bool:
        inm = request.headers.get("if-none-match")
        return inm == self.generate_etag(request)
