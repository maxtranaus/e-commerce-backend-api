from fastapi import FastAPI

from app.routers import (
    auth_api,
    cart_api,
    category_api,
    order_api,
    product_api,
    user_api,
)

app = FastAPI()


app.include_router(auth_api.router)
app.include_router(user_api.router)
app.include_router(category_api.router)
app.include_router(product_api.router)
app.include_router(cart_api.router)
app.include_router(order_api.router)
