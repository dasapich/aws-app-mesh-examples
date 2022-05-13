""" Function to deploy the canary version. """
import logging
import boto3
from botocore.exceptions import ClientError

# Logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# Client connections
APPMESH_CLIENT = boto3.client("appmesh")


def _perform_canary_testing(event, new_vn, header_key, header_value):
    """Function to perform Canary Testing."""

    new_vn = event["MicroserviceName"] + "-" + event["Sha"]
    try:
        if event["Protocol"].lower() == "http":
            spec = {
                "httpRoute": {
                    "action": {
                        "weightedTargets": [{"virtualNode": new_vn, "weight": 1}]
                    },
                    "match": {
                        "prefix": "/",
                        "headers": [
                            {"name": header_key, "match": {"exact": header_value}}
                        ],
                    },
                    "retryPolicy": {
                        "httpRetryEvents": [
                            "server-error",
                            "client-error",
                            "gateway-error",
                        ],
                        "maxRetries": 2,
                        "perRetryTimeout": {"unit": "ms", "value": 2000},
                    },
                }
            }
        else:
            # Only HTTP supported!
            raise BaseException("Only HTTP supported")

        APPMESH_CLIENT.create_route(
            meshName=event["EnvironmentName"],
            routeName=event["MicroserviceName"] + "-" + "testing-route",
            spec=spec,
            virtualRouterName=event["MicroserviceName"] + "-" + "vr",
        )
        return True
    except ClientError as _ex:
        LOGGER.error("Create new route for canary testing failed")
        return False


def lambda_handler(event, _context):
    """Main handler."""

    LOGGER.info("Setting up canary testing")
    route = event["Protocol"] + "Route"
    entries = APPMESH_CLIENT.describe_route(
        meshName=event["EnvironmentName"],
        routeName=event["MicroserviceName"] + "-" + "route",
        virtualRouterName=event["MicroserviceName"] + "-" + "vr",
    )["route"]["spec"][route]["action"]["weightedTargets"]
    print(entries)
    for entry in entries:
        if entry["virtualNode"].endswith(event["Sha"]):
            new_vn = entry["virtualNode"]
            # TODO: Change to parameters in specfiles/deploy.json (hard code for now)
            header_key = "counter_no"
            header_value = "88888"
            if _perform_canary_testing(event, new_vn, header_key, header_value):
                LOGGER.info(
                    "Performed the Canary Testing for HTTP header {} matching {}".format(
                        header_key, header_value
                    )
                )
            else:
                return {"status": "FAIL"}
