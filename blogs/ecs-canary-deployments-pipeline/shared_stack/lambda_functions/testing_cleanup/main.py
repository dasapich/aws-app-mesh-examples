""" Function to deploy the canary version. """
import logging
import boto3
from botocore.exceptions import ClientError

# Logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# Client connections
APPMESH_CLIENT = boto3.client("appmesh")


def _cleanup_canary_testing(event):
    """Function to clean up Canary Testing."""

    try:
        meshName = event["EnvironmentName"]
        virtualRouterName = event["MicroserviceName"] + "-" + "vr"

        routes = APPMESH_CLIENT.list_routes(
            meshName=meshName, virtualRouterName=virtualRouterName
        )["routes"]

        for route in routes:
            if route["routeName"].endswith("testing-route"):
                APPMESH_CLIENT.delete_route(
                    meshName=meshName,
                    virtualRouterName=virtualRouterName,
                    routeName=route["routeName"],
                )
        return True
    except ClientError as _ex:
        LOGGER.error("Delete canary testing route failed")
        return False


def lambda_handler(event, _context):
    """Main handler."""

    LOGGER.info("Cleaning up canary testing")
    if _cleanup_canary_testing(event):
        LOGGER.info("Cleaned up the Canary Testing")
    else:
        return {"status": "FAIL"}
