import asyncio
import httpx


async def make_withdrawal(request_name: str):
    async with httpx.AsyncClient() as client:
        print(f"🚀 Firing first request {request_name}...")
        response = await client.post(
            "http://127.0.0.1:8000/api/v1/withdrawals/demo-concurrency",
            json={"account_id": 1, "amount": 1.00, "name": "ATM Withdrawal"},
        )
        print(
            f"🏁 {request_name} finished! first with Server returned: {response.json()}"
        )


async def make_withdrawal2(request_name: str):
    async with httpx.AsyncClient() as client:
        print(f"🚀 Firing first request {request_name}...")
        response = await client.post(
            "http://127.0.0.1:8000/api/v1/withdrawals/demo-concurrency",
            json={
                "account_id": 1,
                "amount": 1.00,
                "name": "Cash Withdrawal",
                "reference": "ATM-REF-12345",
            },
        )
        print(
            f"🏁 {request_name} finished! second with Server returned: {response.json()}"
        )


async def main():
    # ⚡ Run both withdrawal requests concurrently
    await asyncio.gather(
        make_withdrawal("Request_A"),  # Wants to withdraw $30
        make_withdrawal("Request_B"),  # Wants to withdraw $20
    )


if __name__ == "__main__":
    asyncio.run(main())
