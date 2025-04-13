"""API module for interacting with the Ultramsg API."""

import logging
from typing import Optional

import requests


class UltramsgAPI:
    """Class for interacting with the Ultramsg API."""

    logger = logging.getLogger(__name__)

    def __init__(self, api_url: str, instance_id: str, token: str) -> None:
        """
        Initializes the UltramsgAPI class with API URL, instance ID, and token.

        :param api_url: The base URL of the Ultramsg API.
        :param instance_id: The instance ID for the Ultramsg API.
        :param token: The token for accessing the Ultramsg API.
        """
        self.api_url = api_url
        self.instance_id = instance_id
        self.token = token

    @staticmethod
    def parse_inbound_message(request: dict) -> dict:
        """Parses message request payload and returns extracted values."""
        data = {}

        if request:
            data["message_id"] = request["data"]["id"]
            data["instance_id"] = request["instanceId"]
            data["event_type"] = request["event_type"]
            data["time"] = request["data"]["time"]
            data["author"] = str(request["data"]["author"].replace("@c.us", ""))
            data["from_self"] = request["data"]["fromMe"]
            data["pushname"] = request.get("data", {}).get("pushname", "")
            data["sender"] = str(request["data"]["from"].replace("@c.us", ""))
            data["receiver"] = str(request["data"]["to"].replace("@c.us", ""))
            data["parent_message"] = request["data"].get("quotedMsg", "")
            data["message_type"] = request["data"].get("type", "unknown")
            data["body"] = request["data"]["body"]
            data["media"] = request.get("data", {}).get("media", "")
            data["location"] = request.get("data", {}).get("location", "")
            if data["message_type"] != "chat":
                data["caption"] = data["body"]

        return data

    def send_rest_request(
        self,
        endpoint: str,
        data: Optional[dict] = None,
        method: str = "POST",
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Sends a REST API request and returns a structured response if successful, None otherwise.

        :param endpoint: The API endpoint to call.
        :param method: HTTP method to use (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        :param headers: Optional headers to include in the request. Defaults to JSON content type.
        :param data: Optional data payload for requests (typically POST/PUT). Sent in the request body.
        :param params: Optional query parameters for GET requests. Appended to the URL.
        :return: A dictionary containing either the response data if successful, or None if failed.
        """
        if headers is None:
            headers = {"Content-Type": "application/json"}

        url = f"{self.api_url}/{self.instance_id}/{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, headers=headers, json=data, params=params
            )

            if response.status_code // 100 == 2:
                result = response.json()
                if result and result.get("error", False):
                    self.logger.error(
                        f"UltraMsg request error: {result.get('error', False)}"
                    )
                return result
            else:
                error = f"Request failed with status code {response.status_code}, response: {response.text}"
                self.logger.error(error)
                return {"error": error}

        except requests.exceptions.RequestException as e:
            error = f"Error while executing Ultramsg call: {str(e)}"
            self.logger.error(error)
            return {"error": error}

    def update_instance_settings(
        self,
        webhook_url: str,
        send_delay: int,
        webhook_message_received: str,
        webhook_message_create: str,
        webhook_message_ack: str,
        webhook_message_download_media: str,
    ) -> dict:
        """Updates the instance settings.

        :param webhook_url: The URL of the webhook.
        :param send_delay: The delay between sending messages.
        :param webhook_message_received: The webhook message received.
        :param webhook_message_create: The webhook message create.
        :param webhook_message_ack: The webhook message ack.
        :param webhook_message_download_media: The webhook message download media.
        """
        data = {
            "token": self.token,
            "sendDelay": send_delay,
            "webhook_url": webhook_url,
            "webhook_message_received": webhook_message_received,
            "webhook_message_create": webhook_message_create,
            "webhook_message_ack": webhook_message_ack,
            "webhook_message_download_media": webhook_message_download_media,
        }

        return self.send_rest_request(endpoint="instance/settings", data=data)

    def send_text_message(
        self, phone_number: str, message: str, msg_id: str = ""
    ) -> dict:
        """Sends a text message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "body": message,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/chat", data=data)

    def send_image(
        self, phone_number: str, media_url: str, caption: str = "", msg_id: str = ""
    ) -> dict:
        """Sends an image message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "image": media_url,
            "caption": caption,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/image", data=data)

    def send_sticker(self, phone_number: str, media_url: str, msg_id: str = "") -> dict:
        """Sends a sticker message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "sticker": media_url,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/sticker", data=data)

    def send_document(
        self,
        phone_number: str,
        media_url: str,
        filename: str,
        caption: str = "",
        msg_id: str = "",
    ) -> dict:
        """Sends a document message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "filename": filename,
            "document": media_url,
            "caption": caption,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/document", data=data)

    def send_audio(self, phone_number: str, media: str, msg_id: str = "") -> dict:
        """Sends an audio message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "audio": media,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/audio", data=data)

    def send_voice(self, phone_number: str, media: str, msg_id: str = "") -> dict:
        """Sends a voice message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "audio": media,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/voice", data=data)

    def send_video(
        self, phone_number: str, media_url: str, caption: str = "", msg_id: str = ""
    ) -> dict:
        """Sends a video message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "video": media_url,
            "caption": caption,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/video", data=data)

    def send_contact(self, phone_number: str, contact: str, msg_id: str = "") -> dict:
        """Sends a contact message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "contact": contact,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/contact", data=data)

    def send_location(
        self, phone_number: str, address: str, lat: float, lng: float, msg_id: str = ""
    ) -> dict:
        """Sends a location message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "address": address,
            "lat": lat,
            "lng": lng,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/location", data=data)

    def send_vcard(self, phone_number: str, vcard: str, msg_id: str = "") -> dict:
        """Sends a vcard message to a phone number."""
        data = {
            "token": self.token,
            "to": phone_number,
            "vcard": vcard,
            "msgId": msg_id,
        }
        return self.send_rest_request(endpoint="messages/vcard", data=data)

    def send_reaction(self, msg_id: str, reaction: str) -> dict:
        """Sends a reaction to a message."""
        data = {"token": self.token, "msgId": msg_id, "emoji": reaction}
        return self.send_rest_request(endpoint="messages/reaction", data=data)

    def delete_message(self, msg_id: str) -> dict:
        """Deletes a message."""
        data = {"token": self.token, "msgId": msg_id}
        return self.send_rest_request(endpoint="messages/delete", data=data)

    def get_instance_status(self) -> dict:
        """Gets the status of the instance."""
        data = {"token": self.token}
        return self.send_rest_request(
            endpoint="instance/status", method="GET", data=data
        )

    def get_qr_image(self) -> dict:
        """Gets the QR image."""
        data = {"token": self.token}
        return self.send_rest_request(endpoint="instance/qr", method="GET", data=data)

    def logout(self) -> dict:
        """Logs out of WhatsApp."""
        data = {"token": self.token}
        return self.send_rest_request(endpoint="instance/logout", data=data)

    def restart_instance(self) -> dict:
        """Restarts the instance."""
        data = {"token": self.token}
        return self.send_rest_request(endpoint="instance/restart", data=data)
