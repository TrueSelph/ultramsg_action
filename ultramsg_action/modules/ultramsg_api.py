"""API module for interacting with the Ultramsg API."""

import base64
import logging
import mimetypes
import os
import traceback
from typing import Dict, Optional

import requests


class UltramsgAPI:
    """Class for interacting with the Ultramsg API."""

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        api_url: str,
        instance_id: str,
        token: str,
        webhook_properties: dict,
        timeout: int = 10,
    ) -> None:
        """
        Initializes the UltramsgAPI class with API URL, instance ID, and token.

        :param api_url: The base URL of the Ultramsg API.
        :param instance_id: The instance ID for the Ultramsg API.
        :param token: The token for accessing the Ultramsg API.
        """
        self.api_url = api_url
        self.instance_id = instance_id
        self.token = token
        self.timeout = timeout
        self.webhook_properties = webhook_properties

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
        method: str = "POST",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        json_body: bool = True,
        use_full_url: bool = False,
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

        url = endpoint if use_full_url else f"{self.api_url}/{endpoint}"

        json_payload = data if json_body else None
        body = None if json_body else data

        try:

            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=body,
                json=json_payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.Timeout as e:
            self.logger.error(f"Request timed out after {self.timeout} seconds: {e}")
            return {"error": f"Timeout after {self.timeout} seconds"}
        except requests.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            error_details = (
                e.response.json() if e.response and e.response.content else None
            )
            return {"error": str(e), "details": error_details}
        except Exception as e:
            self.logger.error(f"Unexpected error: {traceback.format_exc()}")
            return {"error": str(e)}

    def register_session(
        self,
        webhook_url: str,
    ) -> dict:
        """Updates the instance settings.

        :param webhook_url: The URL of the webhook.
        """
        data = self.webhook_properties
        data["token"] = self.token
        data["webhook_url"] = webhook_url

        return self.send_rest_request(endpoint="instance/settings", data=data)

    def send_message(self, phone: str, message: str, message_id: str = "") -> dict:
        """Sends a text message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "body": message,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/chat", data=data)

    def send_image(
        self, phone: str, media_url: str, caption: str = "", message_id: str = ""
    ) -> dict:
        """Sends an image message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "image": media_url,
            "caption": caption,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/image", data=data)

    def send_sticker(self, phone: str, media_url: str, message_id: str = "") -> dict:
        """Sends a sticker message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "sticker": media_url,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/sticker", data=data)

    def send_document(
        self,
        phone: str,
        media_url: str,
        filename: str,
        caption: str = "",
        message_id: str = "",
    ) -> dict:
        """Sends a document message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "filename": filename,
            "document": media_url,
            "caption": caption,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/document", data=data)

    def send_audio(self, phone: str, media: str, message_id: str = "") -> dict:
        """Sends an audio message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "audio": media,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/audio", data=data)

    def send_voice(self, phone: str, media: str, message_id: str = "") -> dict:
        """Sends a voice message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "audio": media,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/voice", data=data)

    def send_video(
        self, phone: str, media_url: str, caption: str = "", message_id: str = ""
    ) -> dict:
        """Sends a video message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "video": media_url,
            "caption": caption,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/video", data=data)

    def send_contact(self, phone: str, contact: str, message_id: str = "") -> dict:
        """Sends a contact message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "contact": contact,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/contact", data=data)

    def send_location(
        self, phone: str, address: str, lat: float, lng: float, message_id: str = ""
    ) -> dict:
        """Sends a location message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "address": address,
            "lat": lat,
            "lng": lng,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/location", data=data)

    def send_vcard(self, phone: str, vcard: str, message_id: str = "") -> dict:
        """Sends a vcard message to a phone number."""
        data = {
            "token": self.token,
            "to": phone,
            "vcard": vcard,
            "msgId": message_id,
        }
        return self.send_rest_request(endpoint="messages/vcard", data=data)

    def send_reaction(self, message_id: str, reaction: str) -> dict:
        """Sends a reaction to a message."""
        data = {"token": self.token, "msgId": message_id, "emoji": reaction}
        return self.send_rest_request(endpoint="messages/reaction", data=data)

    def delete_message(self, message_id: str) -> dict:
        """Deletes a message."""
        data = {"token": self.token, "msgId": message_id}
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

    def logout_session(self) -> dict:
        """Logs out of WhatsApp."""
        data = {"token": self.token}
        return self.send_rest_request(endpoint="instance/logout", data=data)

    def restart_instance(self) -> dict:
        """Restarts the instance."""
        data = {"token": self.token}
        return self.send_rest_request(endpoint="instance/restart", data=data)

    @staticmethod
    def file_url_to_base64(file_url: str) -> Optional[str]:
        """
        Downloads file from any web-URL and encodes contents as base64.
        Does not store the file to any persistent file or storage backend.
        """
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            encoded = base64.b64encode(response.content).decode("utf-8")
            return encoded
        except Exception as ex:
            UltramsgAPI.logger.error(f"Error downloading or encoding file: {ex}")
            return None

    @staticmethod
    def get_file_type(
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> dict:
        """
        Determines the MIME type of a file or URL and categorizes it into common file types
        (image, document, audio, video, unknown).
        """

        detected_mime_type = None

        if file_path:
            # Use mimetypes to guess MIME type based on file extension
            detected_mime_type, _ = mimetypes.guess_type(file_path)
        elif url:
            # Make a HEAD request to get the Content-Type header
            try:
                response = requests.head(url, allow_redirects=True)
                detected_mime_type = response.headers.get("Content-Type")
            except requests.RequestException as e:
                UltramsgAPI.logger.error(f"Error making HEAD request: {e}")
        else:
            # Fallback to initial MIME type if provided
            detected_mime_type = mime_type

        # MIME type categories
        mime_categories = {
            "image": [
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/bmp",
                "image/webp",
                "image/tiff",
                "image/svg+xml",
                "image/x-icon",
                "image/heic",
                "image/heif",
                "image/x-raw",
            ],
            "document": [
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "text/plain",
                "text/csv",
                "text/html",
                "application/rtf",
                "application/x-tex",
                "application/vnd.oasis.opendocument.text",
                "application/vnd.oasis.opendocument.spreadsheet",
                "application/epub+zip",
                "application/x-mobipocket-ebook",
                "application/x-fictionbook+xml",
                "application/x-abiword",
                "application/vnd.apple.pages",
                "application/vnd.google-apps.document",
            ],
            "audio": [
                "audio/mpeg",
                "audio/wav",
                "audio/ogg",
                "audio/flac",
                "audio/aac",
                "audio/mp3",
                "audio/webm",
                "audio/amr",
                "audio/midi",
                "audio/x-m4a",
                "audio/x-realaudio",
                "audio/x-aiff",
                "audio/x-wav",
                "audio/x-matroska",
            ],
            "video": [
                "video/mp4",
                "video/mpeg",
                "video/ogg",
                "video/webm",
                "video/quicktime",
                "video/x-msvideo",
                "video/x-matroska",
                "video/x-flv",
                "video/x-ms-wmv",
                "video/3gpp",
                "video/3gpp2",
                "video/h264",
                "video/h265",
                "video/x-f4v",
                "video/avi",
            ],
        }

        # Handle cases where MIME type cannot be detected
        if not detected_mime_type or detected_mime_type == "binary/octet-stream":
            file_extension = ""
            if file_path:
                _, file_extension = os.path.splitext(file_path)
            elif url:
                _, file_extension = os.path.splitext(url)

            detected_mime_type = mimetypes.types_map.get(
                file_extension.lower(), "unknown/unknown"
            )

        # Categorize MIME type
        for category, mime_list in mime_categories.items():
            if detected_mime_type in mime_list:
                return {"file_type": category, "mime": detected_mime_type}

        # Default to "unknown" if no category matches
        return {"file_type": "unknown", "mime": detected_mime_type}


# # import requests

# # url = "https://api.ultramsg.com/instance58058/instance/settings"
# # payload = {
# #     "token": "1ss7rwu3fkuv3kch",
# #     "sendDelay": "1",
# #     "webhook_url": "",
# #     "webhook_message_received": "",
# #     "webhook_message_create": "",
# #     "webhook_message_ack": "",
# #     "webhook_message_download_media": ""
# # }
# # headers = {'Content-Type': 'application/json'}


# # data= {'method': 'POST', 'url': 'https://api.ultramsg.com/instance58058/instance58058/instance/settings', 'params': None, 'data': None, 'json': {'send_delay': 3, 'webhook_message_received': 'True', 'webhook_message_create': 'False', 'webhook_message_ack': 'True', 'webhook_message_download_media': 'True', 'token': '1ss7rwu3fkuv3kch', 'webhook_url': 'https://cc2e-190-93-39-3.ngrok-free.app/webhook/%7B%22ageCI_id%22%3A%22C%3ApgeCI%3A681bc730d48d1e0266db021a%22%2C%22BDdJAe_GDDI%22%3A%22acIiDCH.jiKaH.JAIGaBHg_acIiDC%22%2C%22laAkeG%22%3A%22JAIGaBHg_iCIeGacI%22%7D'}, 'headers': {'Content-Type': 'application/json'}, 'timeout': 10.0}

# # import requests
# # response = requests.request(
# #     method=data["method"],
# #     url=data["url"],
# #     params=data["params"],
# #     data=data["data"],
# #     json=data["json"],
# #     headers=data["headers"],
# #     timeout=data["timeout"],
# # )
# # print(response.text)


# import requests

# # url = "https://api.ultramsg.com/instance58058/instance/settings"
# # payload = {
# #     "token": "1ss7rwu3fkuv3kch",
# #     "sendDelay": "1",
# #     "webhook_url": "",
# #     "webhook_message_received": "",
# #     "webhook_message_create": "",
# #     "webhook_message_ack": "",
# #     "webhook_message_download_media": ""
# # }
# # headers = {'Content-Type': 'application/json'}

# response = requests.post(url, json=payload, headers=headers)
# print(response.text)
# print(response.json())
