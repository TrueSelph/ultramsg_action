import:py logging;
import:py from logging { Logger }
import:py from jivas.agent.modules.agentlib.utils { Utils }
import:py from .modules.ultramsg_api { UltramsgAPI }
import:jac from jivas.agent.action.action { Action }
import:jac from jivas.agent.action.interact { interact }
import:jac from jivas.agent.action.interact_graph_walker { interact_graph_walker }
import:jac from jivas.agent.core.agent { Agent }
import:jac from jivas.agent.memory.frame { Frame }
import:jac from jivas.agent.memory.memory { Memory }

walker ultramsg_interact :interact_graph_walker: {
    # called via a webhook whenever there are verification requests or inbound messages
    # when activated, it will trigger the whatsapp interact action to communicate

    # set up logger
    static has logger:Logger = logging.getLogger(__name__);

    has headers:dict = {};
    # main param for incoming webhook data
    has params:dict = {};
    # main param for outgoing webhook data
    has response:dict = {};

    can on_agent with Agent entry {

        # handle request here to ensure it's worth the walk
        if(not self.params) {
            Jac.get_context().status = 200;
            disengage;
        }

        if(not (action_node := here.get_actions().get(action_label='UltramsgAction'))) {
            Jac.get_context().status = 200;
            disengage;
        }

        if(not action_node.enabled) {
            Jac.get_context().status = 200;
            disengage;
        }

        # parse data if we've gotten so far..
        data = action_node.api().parse_inbound_message(request = self.params);
        if(not data) {
            Jac.get_context().status = 200;
            disengage;
        }

        # ignore loopback messages i.e. messages where sender and receiver are the same
        if(data['sender'] == data['receiver']) {
            Jac.get_context().status = 200;
            disengage;
        }

        # with message_ack, the sender is the agent and the receiver is the user
        if(data['event_type'] == 'message_ack') {
            # if this is human messaging as the AI, author would be set
            if(data['author']) {
                frame_node = here.get_memory().get_frame(agent_id = here.id, session_id = data["receiver"], force_session=True);
                self.logger.debug('inserting human message into AI context');
                frame_node.add_unprompted_interaction(message = data["body"], channel = "whatsapp");
            }
            disengage;
        }

        # set agent phone number
        action_node.phone_number = data["receiver"];

        if(action_node.ignore_newsletters and "@newsletter" in data["sender"]) {
            Jac.get_context().status = 200;
            disengage;
        }

        # determine if phone number has access
        if(access_control_action_node := here.get_actions().get(action_label='AccessControlAction')) {

            access = access_control_action_node.has_action_access(
                session_id=data['sender'],
                action_label='UltramsgAction',
                channel='whatsapp'
            );

            if not access {
                Jac.get_context().status = 200;
                disengage;
            }
        }

        # init the frame here so we can have it all set up to add the sender info from data
        # we have to force session to get frame to use the session_id we supply, so we can track whatsapp user by number
        frame_node = here.get_memory().get_frame(agent_id = here.id, session_id = data["sender"], force_session=True);

        if(action_node.use_pushname) {
            # grab and save the sender name in a frame variable
            frame_node.set_user_name(data['pushname']);
        }

        # handle chat message requests
        if(data['message_type'] == 'chat') {
            self.handle_chat_message(
                data = data,
                agent_node = here,
                frame_node = frame_node,
                action_node = action_node
            );
        }

        # handle voicenote requests
        if(data['message_type'] in ['ptt']) {
            self.handle_voicenote_message(
                data = data,
                agent_node = here,
                frame_node = frame_node,
                action_node = action_node
            );
        }

        # handle media requests
        if(data['message_type'] in ['audio', 'document', 'image', 'video']) {
            self.handle_media_message(
                data = data,
                agent_node = here,
                frame_node = frame_node,
                action_node = action_node
            );
        }

        # handle location requests
        if(data['message_type'] in ['location']) {
            self.handle_location_message(
                data = data,
                agent_node = here,
                frame_node = frame_node,
                action_node = action_node
            );
        }

    }

    can is_directed_message(data:dict) -> bool {
        # interprets the data to determine whether it's a direct group reply or valid direct chat with content

        if(data['author']) {
            # this means we are in a group..only respond if the message starts with @[agent name]
            callout = ( ("@"+data['receiver']).replace("@c.us", "") ).lower();
            callout_index = ((data['body']).lower()).find(callout);
            if( callout_index == -1 ) {
                # then we ignore unless they are directly calling us out in the group...
                return False;
            } else {
                # remove the callout from the message...
                data['body'] = (data['body']).replace(callout, "");
                return True;
            }
        }

        return True;
    }

    can handle_chat_message(data:dict, agent_node:Agent, frame_node:Frame, action_node:Action) {

        if(self.is_directed_message(data)) {
            # only respond if we have a message and if we are messaged with @ in groups

            message = (root spawn interact(
                utterance = data['body'],
                agent_id = agent_node.id,
                session_id = frame_node.session_id,
                verbose = False,
                reporting = False,
                channel = "whatsapp",
                data = [{"label": "whatsapp_chat", "meta": {}, "content": data}]
            )).message;

            # handle reply
            parent_message_id = "";
            if(data.get("parent_message")){
                parent_message_id = data.get("message_id");
            }

            action_node.send_message(session_id=frame_node.session_id, message=message, parent_message_id=parent_message_id);
        }
    }

    can handle_voicenote_message(data:dict, agent_node:Agent, frame_node:Frame, action_node:Action) {
        # This action downloads the voicenote audio transcribes it and passes it to interact walker as text to be processed

        if(not data['author']) { # sidestep voicenotes in group chats

            message = None;
            transcription = None;
            interact_object = None;

            # load stt action
            if(stt_action := agent_node.get_stt_action()) {
                transcription = stt_action.invoke(
                    audio_url = data['media']
                );
            } else {
                self.logger.error('unable to load speech-to-text action');
            }

            if(transcription) {
                interact_object = (root spawn interact(
                    utterance = transcription,
                    agent_id = agent_node.id,
                    session_id = frame_node.session_id,
                    verbose = False,
                    reporting = False,
                    tts = True,
                    channel = "whatsapp",
                    data = [{"label": "whatsapp_voicenote", "meta": {'message_type': data['message_type']}, "content": data['media']}]
                ));
            }

            # now we grab the response and send it
            if(interact_object) {

                has_tts_response = False;
                parent_message_id = interact_object.message.get_meta('parent_message_id');

                # check for TTS result in interact_object since tts flag was set to True
                audio_url = interact_object.response.get('response', {}).get('audio_url');

                if(audio_url) {
                    audio_base64 = UltramsgAPI.file_url_to_base64(audio_url);
                    # sends audio via message using base64
                    response = action_node.api().send_audio(phone_number=frame_node.session_id, media = audio_base64);

                    if response.get("sent") == 'true' {
                        has_tts_response = True;
                    }
                }

                if(not has_tts_response) {
                    # fall back on text reply if no tts response generated
                    action_node.send_message(session_id=frame_node.session_id, message=interact_object.message);
                }

            }
        }
    }

    can handle_media_message(data:dict, agent_node:Agent, frame_node:Frame, action_node:Action) {
        # add document resource to data node in interaction
        if(self.is_directed_message(data)) {
            message = (root spawn interact(
                utterance = data['caption'], # if data['caption'] else f'sent {data['message_type']} file in the chat',
                agent_id = agent_node.id,
                session_id = frame_node.session_id,
                verbose = False,
                reporting = False,
                channel = "whatsapp",
                data = [{"label": "whatsapp_media", "meta": {}, "content": data}]
            )).message;

            # handle reply
            parent_message_id = "";
            if(data.get("parent_message")){
                parent_message_id = data.get("message_id");
            }

            action_node.send_message(session_id=frame_node.session_id, message=message, parent_message_id=parent_message_id);
        }
    }

    can handle_location_message(data:dict, agent_node:Agent, frame_node:Frame, action_node:Action) {
        # add document resource to data node in interaction
        if(self.is_directed_message(data)) {
            message = (root spawn interact(
                utterance = "The user sent their location.",
                agent_id = agent_node.id,
                session_id = frame_node.session_id,
                verbose = False,
                reporting = False,
                channel = "whatsapp",
                data = [{"label": "whatsapp_location", "meta": {}, "content": data}]
            )).message;

            # handle reply
            parent_message_id = "";
            if(data.get("parent_message")){
                parent_message_id = data.get("message_id");
            }

            action_node.send_message(session_id=frame_node.session_id, message=message, parent_message_id=parent_message_id);
        }
    }
}
