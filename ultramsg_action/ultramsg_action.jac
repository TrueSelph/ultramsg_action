import:py os;
import:py traceback;
import:py logging;
import:py from logging { getLogger as Logger }
import:py from .modules.ultramsg_api { UltramsgAPI }
import:py from jivas.agent.modules.agentlib.utils { Utils }
import:py from jvserve.lib.agent_interface { AgentInterface }
import:jac from jivas.agent.action.action { Action }
import:jac from jivas.agent.memory.interaction_response { MessageType }

node UltramsgAction :Action: {
    # houses configurations per agent for whatsapp api communications provided by ultramsg api

    # set up logger
    static has logger:Logger = logging.getLogger(__name__);

    has api_url:str = "https://api.ultramsg.com";
    has instance_id:str = ""; # the ultramsg instance ID
    has token:str = ""; # the ultramsg token
    has phone_number:str = ""; # the whatsapp phone number
    has base_url:str = "";  # the base url for the JIVAS instance
    has webhook_url:str = ""; # the generated webhook url
    has webhook_properties:dict = {"send_delay": 3, "webhook_message_received": "True", "webhook_message_create": "False", "webhook_message_ack": "True", "webhook_message_download_media": "True"};
    has chunk_length:int = 3500;
    # when set, the wa push name value is used as the user name
    has use_pushname:bool = True;
    has ignore_newsletters:bool = True;

    can on_register {

        if (not self.base_url) {
            # default to jivas base url in environment
            self.base_url = os.environ.get('JIVAS_BASE_URL');
        }

        if(self.enabled) {
            self.enabled = self.register_ultramsg_webhook();
        }
    }

    can on_enable() {
        # check if enabled
        if(self.enabled) {
            # register polls webhook
            self.enabled = self.register_ultramsg_webhook();
        }
    }

    can api() -> UltramsgAPI {
        # load the ultramsg api instance

        return UltramsgAPI(
            instance_id=self.instance_id,
            token=self.token,
            api_url=self.api_url
        );

    }

    can register_ultramsg_webhook() {
        # setup procedure for webhook registration on ultramsg api

        success = True;

        agent_id = self.get_agent().id;
        module_root = self.get_module_root();
        # generate webhook key
        webhook_key = AgentInterface.encrypt_webhook_key(agent_id=agent_id, module_root=module_root, walker="ultramsg_interact");

        if(self.base_url and webhook_key) {
            # complete the full webhook url
            self.webhook_url = f'{self.base_url}/webhook/{webhook_key}';
            self.logger.debug(f'ultramsg webhook url: {self.webhook_url}');

            result = self.api().update_instance_settings(
                webhook_url=self.webhook_url,
                send_delay=self.webhook_properties["send_delay"],
                webhook_message_received=self.webhook_properties["webhook_message_received"],
                webhook_message_create=self.webhook_properties["webhook_message_create"],
                webhook_message_ack=self.webhook_properties["webhook_message_ack"],
                webhook_message_download_media=self.webhook_properties["webhook_message_download_media"]
            );

            if('error' in result) {
                success = False;
            }

        } else {
            success = False;
            self.logger.error('unable to generate webhook url for Ultramsg, missing required parameters');
        }

        return success;
    }

    can sanitize_message(message:str) {
        return message.replace("**", "*").replace("<br/>", "\n").replace("<b>", "*").replace("</b>", "*");
    }

    can send_message(session_id:str, message:InteractionMessage, parent_message_id:str = "") {
        # processes an agent response payload format and sends an ultramsg message to a specified session_id via the action

        if(message and session_id) {
            if(not parent_message_id){
                parent_message_id = message.get_meta('parent_message_id');
            }

            if (message.get_type() == MessageType.SILENCE.value) {}
            elif(message.get_type() == MessageType.TEXT.value) {
                content = self.sanitize_message(message = message.get_content());
                outgoing = Utils.chunk_long_message(message=content, max_length = self.chunk_length, chunk_length = self.chunk_length);

                for chunk in outgoing {
                    self.api().send_text_message(phone_number=session_id, message=chunk, msg_id=parent_message_id);
                }
            } elif(message.get_type() == MessageType.MEDIA.value) {
                mime_type = Utils.get_mime_type(mime_type=message.mime);
                if(mime_type['file_type'] == "document") {
                    content = self.sanitize_message(message = message.get_content());
                    self.api().send_document(phone_number= session_id, media_url=message.data.get('url'), file_name=message.data.get('file_name'), caption = content);
                } elif(mime_type['file_type'] == "image") {
                    content = self.sanitize_message(message = message.get_content());
                    self.api().send_image(phone_number=session_id, media_url=message.data.get('url'), caption = content);
                } elif(mime_type['file_type'] == "video") {
                    content = self.sanitize_message(message = message.get_content());
                    self.api().send_video(phone_number=session_id, media_url=message.data.get('url'), caption = content);
                }
            } elif(message.get_type() == MessageType.MULTI.value) {
                for message_item in message.get_content_items() {
                    if(message_item.get_type() == MessageType.TEXT.value) {
                        content = self.sanitize_message(message = message_item.get_content());
                        outgoing = Utils.chunk_long_message(message=content, max_length = self.chunk_length, chunk_length = self.chunk_length);

                        for chunk in outgoing {
                            self.api().send_text_message(phone_number=session_id, message=chunk, msg_id=parent_message_id);
                        }
                    } elif(message_item.get_type() == MessageType.MEDIA.value) {
                        mime_type = Utils.get_mime_type(mime_type=message_item.mime);
                        content = self.sanitize_message(message = message_item.get_content());
                        if(mime_type['file_type'] == "document") {
                            self.api().send_document(phone_number= session_id, media_url=message_item.data.get('url'), file_name=message.data.get('file_name'), caption = content);
                        } elif(mime_type['file_type'] == "image") {
                            self.api().send_image(phone_number=session_id, media_url= message_item.data.get('url'), caption = content);
                        } elif(mime_type['file_type'] == "video") {
                            self.api().send_video(phone_number=session_id, media_url= message_item.data.get('url'), caption = content);
                        }
                    }
                }
            }
        }
    }

    can broadcast_message(message:InteractionMessage, ignore_list:list = []) {
        # processes an agent response payload format and sends an ultramsg message to all session_ids via the action

        if(message) {
            agent_node = self.get_agent();

            if(frames := agent_node.get_memory().get_frames()) {
                # get all frames then proceed to broadcast
                for frame_node in frames {
                    if(frame_node.session_id not in ignore_list) {
                        if(interaction_node := frame_node.get_last_interaction()) {
                            if interaction_node.channel in ['whatsapp'] {
                                self.send_message(session_id = frame_node.session_id, message=message);
                            }
                        }
                    }
                }
            }
        }

    }


    can healthcheck() -> Union[bool, dict] {
        try {
            if (
                self.base_url and
                self.token and
                self.api_url
            ) {
                response = self.api().get_instance_status();
                if (
                    response and
                    response.get("status", {}).get("accountStatus", {}).get("status") == "authenticated" and
                    response.get("status", {}).get("accountStatus", {}).get("substatus") == "connected"
                ) {
                    return True;
                }
                return False;
            }
            return False;
        } except Exception as e {
            self.logger.error(f"An exception occurred in {self.label}:\n{traceback.format_exc()}\n");
            return False;
        }
    }

}
