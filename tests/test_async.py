import random
import pathlib
import json
import subprocess
import threading
import time
import os
import re
import pytest

from paho.mqtt import client as mqtt_client

from openfunction.function_context import FunctionContext
from openfunction.async_server import AsyncApp

TEST_PAYLOAD = {"data": "hello world"}
APP_ID="async.dapr"
TEST_CONTEXT = {
    "name": "test-context",
    "version": "1.0.0",
    "runtime": "Async",
    "port": "8080",
    "inputs": {
        "cron": {
            "uri": "cron_input",
            "componentName": "binding-cron",
            "componentType": "bindings.cron"
        },
        "mqtt_binding": {
            "uri": "of-async-default",
            "componentName": "binding-mqtt",
            "componentType": "bindings.mqtt"
        },
        "mqtt_sub": {
            "uri": "of-async-default-sub",
            "componentName": "pubsub-mqtt",
            "componentType": "pubsub.mqtt"
        }
    },
    "outputs": {
        "cron": {
            "uri": 'cron_output',
            "operation": 'delete',
            "componentName": 'binding-cron',
            "componentType": 'bindings.cron',
        },
        "localfs": {
            "operation": "create",
            "componentName": "binding-localfs",
            "componentType": "bindings.localstorage",
            "metadata": {
                "fileName": "output-file.txt"
            }
        },
        "localfs-delete": {
            "operation": "delete",
            "componentName": "binding-localfs",
            "componentType": "bindings.localstorage",
            "metadata": {
                "fileName": "output-file.txt"
            }
        },
        "mqtt_pub": {
            "uri": 'of-async-default-pub',
            "componentName": 'pubsub-mqtt',
            "componentType": 'pubsub.mqtt',
        }
    }
}

CLIENT_ID = f'of-async-mqtt-{random.randint(0, 1000)}'
BROKER = 'broker.emqx.io'
MQTT_PORT = 1883


@pytest.fixture(scope="module", autouse=True)
def hook(request):
    subprocess.Popen(
        "dapr run -G 50001 -d ./tests/test_data/components/async -a {} -p {} --app-protocol grpc".format(APP_ID, TEST_CONTEXT["port"]), 
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    yield request

    subprocess.Popen("dapr stop {}".format(APP_ID), shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    time.sleep(10)

@pytest.fixture
def client():
    return AsyncApp(FunctionContext.from_json(TEST_CONTEXT))


@pytest.fixture
def mqtt_test_client():
    client = mqtt_client.Client(CLIENT_ID)
    client.connect(BROKER, MQTT_PORT)
    return client


def test_cron(client):
    def cron(client):
      def user_function(context, data):
          assert context.runtime == TEST_CONTEXT["runtime"]
          assert context.inputs["cron"].uri == TEST_CONTEXT["inputs"]["cron"]["uri"]
          context.send("", "cron")
          client.app.stop()

          return
      return user_function

    client.bind(cron(client))
    client.app.run(TEST_CONTEXT["port"])


def test_mqtt_binding(client, mqtt_test_client):
    def binding(client):
        def user_function(context, data):
            context.send(data, "localfs")
            filename = TEST_CONTEXT["outputs"]["localfs"]["metadata"]["fileName"]
            exist = os.path.exists(filename)
            assert exist

            context.send(data, "localfs-delete")
            client.app.stop()

            return
        return user_function
    
    client.bind(binding(client))

    def loop():
        client.app.run(TEST_CONTEXT["port"])

    t = threading.Thread(target=loop, name='LoopThread')
    t.start()

    time.sleep(10)
    mqtt_test_client.publish("of-async-default", payload=json.dumps(TEST_PAYLOAD).encode('utf-8'))

    t.join()


def test_mqtt_subscribe(client, mqtt_test_client):
    def binding(client):
        def user_function(context, data):
            output = 'mqtt_pub'
            # subscribe from mqtt_pub
            def on_message(client, userdata, msg):
                assert msg.payload == json.dumps(TEST_PAYLOAD).encode('utf-8')

                print(msg.payload.decode('utf-8'))

            mqtt_test_client.subscribe(TEST_CONTEXT["outputs"]["mqtt_pub"]["uri"])
            mqtt_test_client.on_message = on_message
            mqtt_test_client.loop_start()

            context.send(json.dumps(TEST_PAYLOAD), output)

            time.sleep(5) 
            mqtt_test_client.loop_stop()

            client.app.stop()
            time.sleep(5) 

            return
        return user_function
    
    client.bind(binding(client))
    
    def loop():
        client.app.run(TEST_CONTEXT["port"])

    t = threading.Thread(target=loop, name='LoopThread')
    t.start()

    time.sleep(10)

    formatted = re.sub(r'"', '\\"', json.dumps(TEST_PAYLOAD))
    subprocess.Popen("dapr publish -i {} -p {} -t {} -d '{}'".format(
        APP_ID, TEST_CONTEXT["inputs"]["mqtt_sub"]["componentName"],
        TEST_CONTEXT["inputs"]["mqtt_sub"]["uri"],
        formatted
        ), shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    t.join()