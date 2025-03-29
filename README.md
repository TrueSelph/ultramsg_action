# Ultramsg Action

![GitHub release (latest by date)](https://img.shields.io/github/v/release/TrueSelph/ultramsg_action)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TrueSelph/ultramsg_action/test-action.yaml)
![GitHub issues](https://img.shields.io/github/issues/TrueSelph/ultramsg_action)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ultramsg_action)
![GitHub](https://img.shields.io/github/license/TrueSelph/ultramsg_action)

JIVAS action wrapper for WhatsApp API communications using the Ultramsg API.

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

- **Jivas:** `^2.0.0`

This package, developed by V75 Inc., provides a JIVAS action wrapper for WhatsApp API communications using the Ultramsg API. As a core action, it simplifies and streamlines interactions with WhatsApp. The package is a singleton and requires the Jivas library version 2.0.0.

---

## How to Use

Below is detailed guidance on how to configure and use the Ultramsg Action.

### Overview

The Ultramsg Action provides an abstraction layer for interacting with WhatsApp via the Ultramsg API. It supports multiple configurations for various use cases, including:

- **Webhook registration** for message handling.
- **Message broadcasting** to multiple recipients.
- **Integration** with Ultramsg for sending text, media, and location messages.

---

### Configuration Structure

The configuration consists of the following components:

### `webhook_properties`

Defines the settings for the webhook, such as message handling and delays.

```python
webhook_properties = {
    "send_delay": 3,
    "webhook_message_received": "True",
    "webhook_message_create": "False",
    "webhook_message_ack": "True",
    "webhook_message_download_media": "True"
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