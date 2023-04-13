import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useState, useEffect } from 'react';
import API from '../api/py_backend';
import Message from './Message';
import { useConversations } from './ConversationsContext';

export default function SelectedConversation() {
    const { selectedConversation, messages, conversationLoading, inStreamAssistantMessage } = useConversations();

    // if inStreamAssistantMessage we need to autoscroll to bottom
    useEffect(() => {
        const conversation = document.querySelector('.conversation');
        if (conversation) {
            conversation.scrollTop = conversation.scrollHeight;
        }
    }, [inStreamAssistantMessage]);
    
    return (
        <Box className="conversation" sx={{ flexGrow: 1, overflowY: 'auto', paddingBottom: '1rem', paddingRight: '1rem' }}>
            {!conversationLoading &&
                selectedConversation &&
                messages.length > 0 &&
                messages.map((message) => {
                    return <Message key={message.id} message={message} />;
                })}
            {!conversationLoading && selectedConversation && inStreamAssistantMessage && (
                <Message key={inStreamAssistantMessage.id} message={inStreamAssistantMessage} />
            )}
        </Box>
    );
}
