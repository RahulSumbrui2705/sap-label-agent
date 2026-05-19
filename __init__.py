import logging
import azure.functions as func
import requests
import base64
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Step 1: Get OAuth token
        token_url = "https://ngvtbuild.authentication.us10.hana.ondemand.com/oauth/token"

        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")

        basic_auth = base64.b64encode(
            f"{client_id}:{client_secret}".encode()
        ).decode()

        token_headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        token_response = requests.post(
            token_url,
            headers=token_headers,
            data={"grant_type": "client_credentials"}
        )

        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        # Step 2: Call BTP Print API
        api_url = "https://cpea-ngvtbuild-dev-glm-print-service.cfapps.us10-001.hana.ondemand.com/shipping/printShippingLabel"

        payload = req.get_json()

        api_response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        return func.HttpResponse(
            json.dumps(api_response.json()),
            status_code=api_response.status_code,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
