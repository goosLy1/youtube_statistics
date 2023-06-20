# from datetime import datetime
# import time

# COUNTER = 0


# def start(time: str):
#     global COUNTER
#     if COUNTER < 1:
#         if time == '00:11':
#             print('program is running...')
#             start.counter += 1


# def func():
#     counter = 0

#     def add(a: int):
#         nonlocal counter
#         counter += a
#         return counter
#     return add

# # start.counter = 0


# # while True:
# if __name__ == "__main__":
#     var = func()
#     print(var(1))
#     print(var(2))
#     print(var(3))

#     # one_time_check = 0
#     # now = datetime.now()
#     # current_time = now.strftime("%H:%M")
#     # start(current_time)

#     # time.sleep(10)

# --------------------------------------------------------------------------------------------
# import os
# import re
# import aiohttp
# import asyncio
# urls = 'https://www.youtube.com/@AriaNightcore'


# async def main():
#     async with aiohttp.ClientSession() as session:
#         async with session.get(urls) as resp:
#             print(resp.status)
#             html = await resp.text()
#             result = re.search(r'channel/[\w|-]{24}', html)
#             id = (result.group()).split('/')[-1]
#             print(id)

# if os.name == 'nt':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(main())

# --------------------------------------------------------------------------------------------
lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
print(lst[:8])

while lst[:8]:
    print(lst.pop(0))
