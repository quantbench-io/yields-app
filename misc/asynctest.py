import asyncio
import time

async def fetch_data(name, delay):
    print(f"{name}: start fetching")
    await asyncio.sleep(delay)
    print(f"{name}: done fetching")
    return f"{name}'s data"

async def main():
    start = time.time()
    results = await asyncio.gather(
        fetch_data("A", 2),
        fetch_data("B", 3)
    )
    print(results)
    print(f"total time: {time.time() - start:.1f}s")


async def main2():
    task_a = asyncio.create_task(fetch_data("A", 2))
    task_b = asyncio.create_task(fetch_data("B", 3))

    print("tasks launched, doing other stuff now...")
    await asyncio.sleep(1)
    print("still waiting on A and B...")

    result_a = await task_a
    result_b = await task_b


async def bad_fetch():
    await asyncio.sleep(1)
    raise ValueError("oops")

async def main3():
    # gather:
    results = await asyncio.gather(
        fetch_data("A", 2),
        bad_fetch()
    )
    # raises ValueError immediately when bad_fetch fails (~1s in)
    # task A is NOT cancelled, but you never get its result — it's abandoned

async def main4():
    # create_task:
    task_a = asyncio.create_task(fetch_data("A", 2))
    task_b = asyncio.create_task(bad_fetch())
    result_a = await task_a        # this succeeds fine, ~2s in
    result_b = await task_b        # THEN this raises ValueError, ~1s in reality but you asked for it second





if __name__ == "__main__":
    asyncio.run(main4())