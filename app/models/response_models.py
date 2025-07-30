from typing import List

# Import the core Beanie Documents they are based on
from app.models.user import User
from app.models.product import Product

# Moved from app/models/user.py
class UserWithProducts(User): # Inherits from the core User Document
    products: List[Product] = []

# Moved from app/models/product.py
class ProductWithUser(Product): # Inherits from the core Product Document
    creator: User # The full User object will be embedded here