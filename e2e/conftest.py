import pytest
import socket
import subprocess
import time
import requests
from playwright.sync_api import sync_playwright


def is_server_running(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def wait_for_server(url: str, timeout: int = 30) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code < 500:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:10000"


@pytest.fixture(scope="session")
def server_process(base_url):
    host = "localhost"
    port = 10000

    if is_server_running(host, port):
        yield None
        return

    process = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "src.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not wait_for_server(base_url, timeout=30):
        process.terminate()
        pytest.skip("Could not start server for E2E tests")

    yield process

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser, base_url, server_process):
    context = browser.new_context()
    page = context.new_page()
    original_goto = page.goto
    page.goto = lambda url, **kwargs: original_goto(f"{base_url}{url}", **kwargs)
    yield page
    context.close()


def pytest_collection_modifyitems(config, items):
    skip_e2e = pytest.mark.skip(reason="E2E tests require running server")
    for item in items:
        if "e2e" in str(item.fspath):
            if not is_server_running("localhost", 10000):
                try:
                    result = subprocess.run(
                        ["uv", "--version"],
                        capture_output=True,
                        timeout=5,
                    )
                    if result.returncode != 0:
                        item.add_marker(skip_e2e)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    item.add_marker(skip_e2e)
