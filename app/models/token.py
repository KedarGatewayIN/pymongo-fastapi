from pydantic import BaseModel
from typing import Optional

# Model for the data within the JWT payload
class TokenData(BaseModel):
    email: Optional[str] = None # We'll store the user's email in the token

# Model for the token returned to the client upon login
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" # Standard token type