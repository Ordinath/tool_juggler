import { createContext, useContext, useState, useEffect } from 'react';
import { StreamHandler } from '../api/stream_handler';
const API_URL = process.env.NEXT_PUBLIC_PY_BACKEND_API_URL;

import API from '../api/py_backend';

const SYSTEM_MESSAGE = `
    You are a helpful assistant and your name is Biggy. You are especially strong in Programming.
    You always consider user's request critically and try to find the best possible solution,
    even if you need to completely overhaul the existing solution to make it better.
    You always follow modern development practices and try to follow best programming principles like 
    KISS, DRY, YAGNI, Composition Over Inheritance, Single Responsibility, Separation of Concerns, SOLID.
    Whenever you provide a multiple lines code snippet, please use the code block syntax - 
    use three backticks (\`\`\`) and specify the programming language.
    For example, to highlight Python code, you would write \`\`\`python.
    For inline code use single backticks (\`) without specifying the language.
    For example, to highlight the word "print", you would write \`print\`.`;

const ConversationsContext = createContext();

export const useConversations = () => {
    return useContext(ConversationsContext);
};

export function ConversationProvider({ children }) {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [conversationLoading, setConversationLoading] = useState(false);
    const [selectedConversationMessages, setSelectedConversationMessages] = useState([]);
    const [inStreamAssistantMessage, setInStreamAssistantMessage] = useState(null);

    // fetch conversations from backend upon page load
    useEffect(() => {
        const fetchConversations = async () => {
            try {
                const fetchedConversations = (await API.getConversations()).reverse();
                console.log(fetchedConversations);
                setConversations(fetchedConversations);
            } catch (error) {
                console.error('Error fetching conversations:', error);
                setConversations([]);
            }
        };
        fetchConversations();
    }, []);

    useEffect(() => {
        const fetchMessages = async () => {
            try {
                let fetchedConversation = await API.getConversation(selectedConversation);
                console.log(fetchedConversation);
                // if this is a new conversation, we add initial system message
                // if (fetchedConversation.messages.length === 0) {
                //     await API.createMessage(selectedConversation, 'system', SYSTEM_MESSAGE, new Date().toISOString());
                //     fetchedConversation = await API.getConversation(selectedConversation);
                //     // setSelectedConversationMessages([newMessage]);
                // }
                setSelectedConversationMessages(fetchedConversation.messages);
            } catch (error) {
                console.error('Error fetching conversations:', error);
                setSelectedConversationMessages([]);
            }
        };
        setConversationLoading(true);
        if (!selectedConversation) {
            setConversationLoading(false);
            return;
        } else {
            fetchMessages();
            setConversationLoading(false);
        }
    }, [selectedConversation]);

    const handleAddNewConversation = async () => {
        console.log('add new conversation');
        // count number of untitled conversations via regex matching 'Untitled' and 'Untitled(n)'
        const untitledConversationCount = conversations.filter((conversation) => conversation.title.match(/Untitled( \(\d+\))?/)).length;
        const newConversationTitle = untitledConversationCount > 0 ? `Untitled (${untitledConversationCount + 1})` : 'Untitled';
        const newConversation = await API.createConversation(newConversationTitle);
        console.log('newConversation', newConversation);
        setConversations([newConversation, ...conversations]);
        setSelectedConversation(newConversation.id);
    };

    const handleDeleteConversation = async (conversationId) => {
        console.log('delete conversation', conversationId);
        await API.deleteConversation(conversationId);
        setConversations(conversations.filter((conversation) => conversation.id !== conversationId));
        setSelectedConversation(null);
    };

    const handleChangeConversationTitle = async (conversationId, newConversationTitle) => {
        console.log('change conversation title', conversationId);
        await API.updateConversation(conversationId, newConversationTitle);
        setConversations(
            conversations.map((conversation) => (conversation.id === conversationId ? { ...conversation, title: newConversationTitle } : conversation))
        );
    };

    const handleSendMessage = async (message) => {
        if (message) {
            await API.createMessage(selectedConversation, 'user', message, new Date().toISOString());
            // here we also need to make the SelectedConversation be aware of the new message
            const newConversation = await API.getConversation(selectedConversation);
            setSelectedConversationMessages(newConversation.messages);
            // and now is the most exciting part - we open a Server-Sent Events connection to the backend to get AI response and  stream the text in a new 'assistant' message within this conversation

            let newAssistantMessage = await API.createMessage(selectedConversation, 'assistant', '\n', new Date().toISOString());
            setInStreamAssistantMessage(newAssistantMessage);
            const endpoint = `${API_URL}/conversations/${selectedConversation}/get_ai_completion`;
            const streamHandler = new StreamHandler({
                model: 'gpt-4', // 'gpt-3.5-turbo', 'gpt-4'
                // model: 'gpt-3.5-turbo', // 'gpt-3.5-turbo', 'gpt-4'
                endpoint,
                assistant_message_id: newAssistantMessage.id,
                onMessage: (text, streamText) => {
                    // console.log('onMessage:', { text, streamText });
                    setInStreamAssistantMessage({ ...newAssistantMessage, content: streamText });
                },
                onFinish: async (streamText) => {
                    // console.log('Stream finished:', streamText);
                    const newConversation = await API.getConversation(selectedConversation);
                    setInStreamAssistantMessage(null);
                    setSelectedConversationMessages(newConversation.messages);
                },
                onError: (err) => {
                    console.error('Stream error:', err);
                },
            });
            streamHandler.start();
        }
    };

    const handleDeleteMessage = async (messageId) => {
        console.log('delete message', messageId);
        await API.deleteMessage(messageId);
        // refresh messages
        let fetchedConversation = await API.getConversation(selectedConversation);
        setSelectedConversationMessages(fetchedConversation.messages);
    };

    const value = {
        conversations,
        setConversations,
        selectedConversation,
        setSelectedConversation,
        messages: selectedConversationMessages,
        setMessages: setSelectedConversationMessages,
        conversationLoading,
        setConversationLoading,
        inStreamAssistantMessage,
        setInStreamAssistantMessage,
        handleAddNewConversation,
        handleDeleteConversation,
        handleChangeConversationTitle,
        handleSendMessage,
        handleDeleteMessage,
    };

    return <ConversationsContext.Provider value={value}>{children}</ConversationsContext.Provider>;
}
