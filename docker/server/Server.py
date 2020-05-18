import asyncio
import socket
import time
import aioredis
from aiohttp import web
REDIS_SERVER = 'redis://redis'


async def redis_connection_possible():
    try:
        redis = await aioredis.create_redis_pool(REDIS_SERVER)
        redis.close()
        await redis.wait_closed()
        return True
    except ConnectionRefusedError as err:
        print("Redis is not available: " + err.__str__())
        return False
    except socket.gaierror as err:
        print("Redis is not available: " + err.__str__())
        return False


async def wait_redis_conn():
    while not await redis_connection_possible():
        time.sleep(1)


async def create_redis_pool(app):
    await wait_redis_conn()
    app['redis'] = await aioredis.create_redis_pool(REDIS_SERVER)


async def destroy_redis_pool(app):
    app['redis'].close
    await app['redis'].wait_closed()


async def handler(request):
    """
    :type request: web.Request
    """
    data = request.query
    # Data validation can be traded for performance
    # Checking that only valid parameters supplied
    if len(data.keys() & {"id", "tag"}) == 2 and len(data) == 2:
        # Insert data in redis
        id_value = data.get("id")
        tag_value = data.get("tag")
        # Checking parameters
        if id_value.isalnum() and tag_value.isalnum():
            data_formatted = id_value + "&" + tag_value
            await app['redis'].execute('incr', data_formatted)
            status = 202
            message = "OK"
        else:
            status = 400
            message = "Parameters should only contain (a-z, A-Z and 0-9)"
    else:
        status = 400
        message = "Should only contain \"id\" and \"tag\" parameters"
    return web.Response(status=status, text=message)


app = web.Application()
app.add_routes([web.get('/', handler)])
app.on_startup.append(create_redis_pool)
app.on_shutdown.append(destroy_redis_pool)
web.run_app(app)
