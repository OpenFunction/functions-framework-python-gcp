import logging

from openfunction.function_context import KNATIVE_RUNTIME_TYPE
from openfunction.function_runtime import OpenFunctionRuntime

def dapr_output_middleware(context):
    """Flask middleware for output binding."""
    def dapr_output_middleware(response):
        if not context or not context.outputs or context.runtime != KNATIVE_RUNTIME_TYPE:
            return response
        
        runtime = OpenFunctionRuntime.parse(context)
        resp = runtime.send(response.get_data(True))
        
        for key, value in resp.items():
            logging.debug("Dapr result for %s: %s", key, value.text())

        return response

    return dapr_output_middleware