# Ultramsg Action

![GitHub release (latest by date)](https://img.shields.io/github/v/release/TrueSelph/ultramsg_action)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TrueSelph/ultramsg_action/test-action.yaml)
![GitHub issues](https://img.shields.io/github/issues/TrueSelph/ultramsg_action)
![GitHub pull requests](https://img.shields.io/github/issues-pr/TrueSelph/ultramsg_action)
![GitHub](https://img.shields.io/github/license/TrueSelph/ultramsg_action)



## Package Information
- **Name:** `jivas/ultramsg_action`
- **Author:** [V75 Inc.](https://v75inc.com/)
- **Architype:** `UltramsgAction`

## Meta Information
- **Title:** Ultramsg Action
- **Group:** core
- **Type:** action

## Configuration
- **Singleton:** true

## Dependencies
- **Jivas:** `~2.0.0-aplha.40`
- **PulseAction:** `~0.0.2`

---

## How to Use

Below is detailed guidance on how to configure and use the Ultramsg Action.

### Overview

The Ultramsg Action provides an abstraction layer for interacting with WhatsApp via the Ultramsg API. It supports multiple configurations for various use cases, including:

- **Webhook registration** for message handling.
- **Message broadcasting** to multiple recipients.
- **Integration** with Ultramsg for sending text, media, and location messages.

### Dynamic Adaptation

The Ultramsg Action includes advanced mechanisms to optimize message delivery:

- **Automatic Interval Adjustment**: Dynamically modifies send intervals based on success rates to ensure efficient delivery.
- **Variable Batch Sizes**: Alternates batch sizes between defined minimum and maximum values for flexibility.
- **Random Jitter**: Introduces slight randomness to sending intervals to prevent detection of predictable patterns.

These features enhance reliability and minimize disruptions during high-volume messaging operations.

---

### Configuration Structure

To use the Ultramsg Action, you need to set up the following configuration parameters. These specify connection and behavioral details.

| Parameter                     | Type   | Description                                                                         | Default |
| ----------------------------- | ------ | ----------------------------------------------------------------------------------- | ------- |
| `api_url`                     | string | The base URL of the Ultramsg API.                                                    | `"https://api.ultramsg.com"`    |
| `instance_id`                 | string | The instance ID for the Ultramsg API.                                                | `""`    |
| `token`                       | string | The token for accessing the Ultramsg API.                                            | `""`    |
| `phone_number`                | string | The whatsapp phone number.                                                          | `""`    |
| `base_url`                    | string | The base URL of the JIVAS instance.                                                  | `""`    |
| `webhook_url`                 | string | The generated webhook URL.                                                          | `""`    |
| `webhook_properties`          | dict   | Settings for the webhook, such as message handling and delays.                       | `{"send_delay": 3, "webhook_message_received": "True", "webhook_message_create": "False", "webhook_message_ack": "True", "webhook_message_download_media": "True"}` |
| `chunk_length`                | int    | The maximum length of message to send. Longer texts are split into subsequent messages. | `3500`  |
| `use_pushname`                | bool   | Use the WhatsApp push name as the user name when set to `True`.                         | `True`  |
| `ignore_newsletters`          | bool   | Ignore newsletter messages when set to `True`.                                        | `True`  |
| `request_timeout`             | float  | Length of time (in seconds) this action waits for the API to complete a request.      | `10.0`  |
| `outbox_base_rate_per_minute` | int    | The base messages per minute (adapts dynamically).                                    | `20`    |
| `outbox_send_interval`        | float  | The current operational delay between batches.                                        | `1.0`   |
| `outbox_min_send_interval`    | float  | The absolute minimum delay (seconds).                                                 | `1.0`   |
| `outbox_max_send_interval`    | float  | The maximum allowed delay (seconds).                                                  | `10.0`  |
| `outbox_min_batch_size`       | int    | The minimum batch size of messages to send from the outbox.                            | `1`     |
| `outbox_max_batch_size`       | int    | The maximum batch size of messages to send from the outbox.                            | `10`    |

---

### Notes on Configuration

- **Parameter Settings**: Ensure all parameters are configured based on your Ultramsg Server and JIVAS deployment requirements.
- **Webhook URL**: The `webhook_url` must be a publicly accessible endpoint to enable event-driven communication from Ultramsg.
- **Outbox Base Rate**: Set `outbox_base_rate_per_minute` to `20` for new numbers. This value should align with WhatsApp's acceptable rate-per-minute limits (default is `20`).
- **Auto Callback**: This when sending or broadcasting messages in batches, this action will trigger your supplied callback upon completion.
- **Batch Size Limits**: For Tier 2 accounts, keep `outbox_max_batch_size` at or below `10` to comply with account limitations.
- **Validation**: Validate your API keys, tokens, and webhook URLs before deploying in production.
- **Chunk Length**: Adjust `chunk_length` if you have use cases that involve very long text messages.
- **Message Filtering**: Use `ignore_newsletters` and `ignore_forwards` to filter out less relevant messages and avoid unnecessary processing.

These guidelines help optimize performance and ensure compliance with WhatsApp's messaging policies.

---


## API Endpoints

### Broadcast Message

**Endpoint:** `/action/walker`
**Method:** `POST`

#### Parameters

```json
{
   "agent_id": "<AGENT_ID>",
   "walker": "broadcast_message",
   "module_root": "actions.jivas.ultramsg_action",
   "args": {
      "message": {
         "message_type": "TEXT|MEDIA|MULTI",
         ...
      },
      "ignore_list": ["session_id_1", ...]
   }
}
```

---

### Send Messages

**Endpoint:** `/action/walker`
**Method:** `POST`

#### Parameters

```json
{
   "agent_id": "<AGENT_ID>",
   "walker": "send_messages",
   "module_root": "actions.jivas.ultramsg_action",
   "args": {
      "messages": [
         // Array of message objects
      ],
      "callback_url": "https://your-callback.url"
   }
}
```

#### Example Request

```json
{
   "messages": [
      {
         "to": "session_id",
         "message": {
            "message_type": "TEXT",
            "content": "Batch message"
         }
      }
   ],
   "callback_url": "https://example.com/status"
}
```

#### Response

Returns a job ID string for tracking.

#### Callback Response

Your callback will receive a JSON payload with the following structure automatically upon job completion:

```json
{
   "status": "success|partial|error",
   "job_id": "<UUID>",
   "processed_count": 10,
   "failed_count": 2,
   "pending_count": 0
}
```

---

### Message Formats

#### TEXT

```json
{
   "message": {
      "message_type": "TEXT",
      "content": "Hello World"
   }
}
```

#### MEDIA

```json
{
   "message": {
      "message_type": "MEDIA",
      "mime": "image/jpeg",
      "content": "Check this!",
      "data": {
         "url": "https://example.com/image.jpg",
         "file_name": "image.jpg"
      }
   }
}
```

#### MULTI

```json
{
   "message": {
      "message_type": "MULTI",
      "content": [
         // Array of TEXT/MEDIA messages
      ]
   }
}
```

---

### Example Configurations

### Basic Configuration for Ultramsg

```python
base_url = "https://your_base_url"
api_key = "your_ultramsg_api_key"
instance_id = "your_instance_id"
phone_number = "your_whatsapp_number"
webhook_properties = {
    "send_delay": 3,
    "webhook_message_received": "True",
    "webhook_message_create": "False",
    "webhook_message_ack": "True",
    "webhook_message_download_media": "True"
}
```

### Best Practices
- Validate your API keys and webhook URLs before deployment.
- Test webhook registration in a staging environment before production use.

---

## 🔰 Contributing

- **🐛 [Report Issues](https://github.com/TrueSelph/ultramsg_action/issues)**: Submit bugs found or log feature requests for the `ultramsg_action` project.
- **💡 [Submit Pull Requests](https://github.com/TrueSelph/ultramsg_action/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/TrueSelph/ultramsg_action
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details open>
<summary>Contributor Graph</summary>
<br>
<p align="left">
    <a href="https://github.com/TrueSelph/ultramsg_action/graphs/contributors">
        <img src="https://contrib.rocks/image?repo=TrueSelph/ultramsg_action" />
   </a>
</p>
</details>

## 🎗 License

This project is protected under the Apache License 2.0. See [LICENSE](./LICENSE) for more information.