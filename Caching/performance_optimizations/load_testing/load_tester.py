from locust import HttpUser, task, between


class ProductLoadTester(HttpUser):
    wait_time = between(1, 2)

    @task(2)
    def get_product_with_cache(self):
        product_id = "1137b5ec-9ac0-40a9-831e-9615e0235bc3"
        self.client.get(f"/api/v1/products/{product_id}?cache=true")

    @task(1)
    def get_product_without_cache(self):
        product_id = "1137b5ec-9ac0-40a9-831e-9615e0235bc3"
        self.client.get(f"/api/v1/products/{product_id}?cache=false")
