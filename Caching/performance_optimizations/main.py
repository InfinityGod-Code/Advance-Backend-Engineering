from fastapi import FastAPI

from routes.product import router as product_router

app_description = """
In this application we will see some of the challenges that we face in order to tackle two most important 
issues in the high traffic scenarios : 
1. Handle huge request simuntaneously.
2. With low latency rate.
3.consistent data accross various platforms.
"""
app = FastAPI(title="Performance Optimizations", description=app_description)
app.include_router(product_router, prefix="/api/v1")


@app.get("/")
def test():
    return {"content": "hello world"}
