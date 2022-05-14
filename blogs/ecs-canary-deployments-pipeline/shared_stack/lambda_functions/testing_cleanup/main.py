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
        APPMESH_CLIENT.delete_route(
            meshName=event["EnvironmentName"],
            routeName=event["MicroserviceName"] + "-" + "testing-route",
            virtualRouterName=event["MicroserviceName"] + "-" + "vr",
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
