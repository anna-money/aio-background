import asyncio

import aiohttp.web
import aiohttp.web_request
import aiohttp.web_response
import pytest
import yarl

import aio_background


@pytest.fixture
async def server_without_jobs(aiohttp_client):
    async def health_check(request: aiohttp.web_request.Request) -> aiohttp.web_response.Response:
        is_healthy = aio_background.aiohttp_is_healthy(request.app)
        return aiohttp.web_response.Response(status=200 if is_healthy else 500)

    app = aiohttp.web.Application()
    app.router.add_get("/", health_check)
    return await aiohttp_client(app)


@pytest.fixture
async def server_with_job(aiohttp_client):
    async def run() -> None:
        await asyncio.sleep(100500)

    async def health_check(request: aiohttp.web_request.Request) -> aiohttp.web_response.Response:
        is_healthy = aio_background.aiohttp_is_healthy(request.app)
        return aiohttp.web_response.Response(status=200 if is_healthy else 500)

    app = aiohttp.web.Application()
    app.router.add_get("/", health_check)
    app.cleanup_ctx.append(aio_background.aiohttp_setup_ctx(aio_background.run(run)))
    return await aiohttp_client(app)


@pytest.fixture
async def server_with_healthy_job(aiohttp_client):
    async def run() -> None:
        await asyncio.sleep(100500)

    async def health_check(request: aiohttp.web_request.Request) -> aiohttp.web_response.Response:
        is_healthy = aio_background.aiohttp_is_healthy(request.app)
        return aiohttp.web_response.Response(status=200 if is_healthy else 500)

    app = aiohttp.web.Application()
    app.router.add_get("/", health_check)
    app.cleanup_ctx.append(aio_background.aiohttp_setup_ctx(aio_background.run(run)))
    return await aiohttp_client(app)


@pytest.fixture
async def server_with_unhealthy_job(aiohttp_client):
    async def run() -> None:
        await asyncio.sleep(0.5)
        raise RuntimeError("Oops")

    async def health_check(request: aiohttp.web_request.Request) -> aiohttp.web_response.Response:
        is_healthy = aio_background.aiohttp_is_healthy(request.app)
        return aiohttp.web_response.Response(status=200 if is_healthy else 500)

    app = aiohttp.web.Application()
    app.router.add_get("/", health_check)
    app.cleanup_ctx.append(aio_background.aiohttp_setup_ctx(aio_background.run(run)))
    return await aiohttp_client(app)


async def test_aiohttp_without_jobs(server_without_jobs):
    async with aiohttp.ClientSession() as client_session:
        url = yarl.URL(f"http://{server_without_jobs.server.host}:{server_without_jobs.server.port}")
        response = await client_session.get(url)
        assert response.status == 200


async def test_aiohttp_with_healthy_job(server_with_healthy_job):
    async with aiohttp.ClientSession() as client_session:
        url = yarl.URL(f"http://{server_with_healthy_job.server.host}:{server_with_healthy_job.server.port}")
        response = await client_session.get(url)
        assert response.status == 200


async def test_aiohttp_with_unhealthy_job(server_with_unhealthy_job):
    async with aiohttp.ClientSession() as client_session:
        url = yarl.URL(f"http://{server_with_unhealthy_job.server.host}:{server_with_unhealthy_job.server.port}")
        response = await client_session.get(url)
        assert response.status == 200
        await asyncio.sleep(1)
        response = await client_session.get(url)
        assert response.status == 500
