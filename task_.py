import asyncio

async def my_task():
    while True:
        i = input("input from task")
        print('TASK', i)
        await asyncio.sleep(0)

async def main():
    task = asyncio.create_task(my_task())
    task.add_done_callback(lambda _: print("Task is done!"))
    # await asyncio.sleep(0)
    print("MAIN")
    await asyncio.sleep(0)
    print("MAIN2")

asyncio.run(main())