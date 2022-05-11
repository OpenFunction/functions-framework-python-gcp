import pathlib
import os
import subprocess
import time

import pytest

from functions_framework import create_app
from openfunction.function_context import FunctionContext

TEST_FUNCTIONS_DIR = pathlib.Path(__file__).resolve().parent / "test_functions"
TEST_RESPONSE = "Hello world!"
FILENAME = "test-binding.txt"
APP_ID="http.dapr"


@pytest.fixture(scope="module", autouse=True)
def dapr(request):
    subprocess.Popen("dapr run -G 50001 -d ./tests/test_data/components/http -a {}".format(APP_ID),
        shell=True)
    time.sleep(3)

    yield request

    subprocess.Popen("dapr stop {}".format(APP_ID), shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    time.sleep(10)


def create_func_context(param):
    return {
        "name": param["name"],
        "version": "1.0.0",
        "runtime": "Knative",
        "outputs": {
            "file": {
                "componentName": "local",
                "componentType": "bindings.localstorage",
                "operation": param["operation"],
                "metadata": {
                    "fileName": FILENAME
                }
            }
        }
    }


@pytest.fixture
def client():
    def return_client(param):
        source = TEST_FUNCTIONS_DIR / "http_basic" / "main.py"
        target = "hello"
        
        context = create_func_context(param)
    
        return create_app(target, source, "http", FunctionContext.from_json(context)).test_client()

    return return_client
    

test_data = [
    {"name": "Save data", "operation": "create", "listable": True},
    {"name": "Get data", "operation": "get", "listable": True},
    {"name": "Delete data", "operation": "delete", "listable": False},
]


@pytest.mark.parametrize("test_data", test_data)
def test_http_binding(client, test_data):
    resp = client(test_data).get("/")

    assert resp.status_code == 200
    assert TEST_RESPONSE == resp.get_data().decode()
    
    exist = os.path.exists(FILENAME)

    assert exist == test_data["listable"]