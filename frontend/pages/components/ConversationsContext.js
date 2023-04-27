import { createContext, useContext, useState, useEffect } from 'react';
import { StreamHandler } from '../api/stream_handler';
import { useClientSideState } from '../hooks/useClientSideState';
import { API_URL } from '../constants';

const MODELS = [
    { name: 'GPT-4 (recommended)', value: 'gpt-4' },
    { name: 'GPT-3.5-TURBO', value: 'gpt-3.5-turbo' },
];

import API from '../api/py_backend';

// const SYSTEM_MESSAGE = `
//     You are a helpful assistant and your name is Biggy. You are especially strong in Programming.
//     You always consider user's request critically and try to find the best possible solution,
//     even if you need to completely overhaul the existing solution to make it better.
//     You always follow modern development practices and try to follow best programming principles like
//     KISS, DRY, YAGNI, Composition Over Inheritance, Single Responsibility, Separation of Concerns, SOLID.
//     Whenever you provide a multiple lines code snippet, please use the code block syntax -
//     use three backticks (\`\`\`) and specify the programming language.
//     For example, to highlight Python code, you would write \`\`\`python.
//     For inline code use single backticks (\`) without specifying the language.
//     For example, to highlight the word "print", you would write \`print\`.`;

const ConversationsContext = createContext();

export const useConversations = () => {
    return useContext(ConversationsContext);
};

export function ConversationProvider({ children }) {
    const [selectedModel, setSelectedModel] = useClientSideState('selectedModel', MODELS[0].value);
    const [conversations, setConversations] = useState([]);
    const [tools, setTools] = useState([]);
    const [secrets, setSecrets] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [conversationLoading, setConversationLoading] = useState(false);
    const [selectedConversationMessages, setSelectedConversationMessages] = useState([]);
    const [inStreamAssistantMessage, setInStreamAssistantMessage] = useState(null);
    const [inStreamAssistantAction, setInStreamAssistantAction] = useState(null);

    const [toasts, setToasts] = useState([]);

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

    // Add a new useEffect to fetch tools from the backend upon page load
    useEffect(() => {
        const fetchTools = async () => {
            try {
                const fetchedTools = await API.getTools();
                setTools(fetchedTools);
            } catch (error) {
                console.error('Error fetching tools:', error);
                setTools([]);
            }
        };
        fetchTools();
    }, []);

    // Fetch secrets from backend upon page load
    useEffect(() => {
        const fetchSecrets = async () => {
            try {
                const fetchedSecrets = await API.getSecrets();
                setSecrets(fetchedSecrets);
                if (
                    !fetchedSecrets.find((secret) => secret.key === 'OPENAI_API_KEY') ||
                    fetchedSecrets.find((secret) => secret.key === 'OPENAI_API_KEY')['value'] === 'TO_BE_PROVIDED'
                ) {
                    addToast('warning', 'No OPENAI_API_KEY secret provided. Please add in the left bottom corner under Settings menu.');
                }
            } catch (error) {
                console.error('Error fetching secrets:', error);
                setSecrets([]);
            }
        };
        fetchSecrets();
    }, []);

    useEffect(() => {
        localStorage.setItem('selectedModel', JSON.stringify(selectedModel));
    }, [selectedModel]);

    useEffect(() => {
        const fetchMessages = async () => {
            try {
                let fetchedConversation = await API.getConversation(selectedConversation);
                console.log(fetchedConversation);
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

    const addToast = (type, message) => {
        console.log('add toast', type, message);
        const newToast = { id: Date.now(), type, message };
        setToasts((prevToasts) => [...prevToasts, newToast]);
    };

    const removeToast = (id) => {
        setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
    };

    const handleAddNewSecret = async (key, value) => {
        console.log('add new secret');
        const newSecret = await API.createSecret(key, value);
        console.log('newSecret', newSecret);
        const newSecrets = await API.getSecrets();
        setSecrets(newSecrets);
    };

    const handleDeleteSecret = async (secretId) => {
        console.log('delete secret', secretId);
        await API.deleteSecret(secretId);
        setSecrets(secrets.filter((secret) => secret.id !== secretId));
    };

    const handleUpdateSecret = async (secretId, key, value) => {
        console.log('update secret', secretId);
        const updatedSecret = await API.updateSecret(secretId, key, value);
        setSecrets(secrets.map((secret) => (secret.id === secretId ? updatedSecret : secret)));
    };

    const toggleTool = async (toolId, toolEnabled) => {
        console.log('toggle tool', toolId, toolEnabled);
        await API.toggleTool(toolId, toolEnabled);
        setTools(tools.map((tool) => (tool.id === toolId ? { ...tool, enabled: !toolEnabled } : tool)));
    };

    const handleDeleteTool = async (toolId) => {
        console.log('delete tool', toolId);
        await API.deleteTool(toolId);
        // get the updated list of tools from the backend
        const fetchedTools = await API.getTools();
        setTools(fetchedTools);
    };

    const createNewConversation = async () => {
        const untitledConversationCount = conversations.filter((conversation) => conversation.title.match(/Untitled( \(\d+\))?/)).length;
        const newConversationTitle = untitledConversationCount > 0 ? `Untitled (${untitledConversationCount + 1})` : 'Untitled';
        const newConversation = await API.createConversation(newConversationTitle);
        return newConversation;
    };

    const handleAddNewConversation = async () => {
        console.log('add new conversation');
        // count number of untitled conversations via regex matching 'Untitled' and 'Untitled(n)'
        const newConversation = await createNewConversation();
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

    const createAndSelectConversation = async () => {
        const newConversation = await createNewConversation();
        setConversations([newConversation, ...conversations]);
        setSelectedConversation((prev) => newConversation.id);
        return newConversation.id;
    };

    const handleSendMessage = async (message) => {
        let currentSelectedConversation = selectedConversation;
        if (!selectedConversation) {
            // if there is no selected conversation, we create a new one and use it\
            currentSelectedConversation = await createAndSelectConversation();
        }
        if (message) {
            await API.createMessage(currentSelectedConversation, 'user', message, new Date().toISOString());
            // here we also need to make the SelectedConversation be aware of the new message
            const newConversation = await API.getConversation(currentSelectedConversation);
            setSelectedConversationMessages(newConversation.messages);

            await getAssistantResponse(currentSelectedConversation);
        }
    };

    // and now is the most exciting part - we open a Server-Sent Events connection to the backend to get AI response and  stream the text in a new 'assistant' message within this conversation
    const getAssistantResponse = async (selectedConversation) => {
        let newAssistantMessage = await API.createMessage(selectedConversation, 'assistant', '\n', new Date().toISOString());
        setInStreamAssistantMessage(newAssistantMessage);
        const endpoint = `${API_URL}/conversations/${selectedConversation}/get_ai_completion`;
        console.log('selectedModel', selectedModel.value);
        const streamHandler = new StreamHandler({
            model: selectedModel,
            // model: 'gpt-4', // 'gpt-3.5-turbo', 'gpt-4'
            endpoint,
            assistant_message_id: newAssistantMessage.id,
            onMessage: (text, streamText) => {
                const regex = /\[\[(.*?)\]\]/;
                const match = text.match(regex);
                if (match) {
                    const action = match[1];
                    setInStreamAssistantAction(action);
                } else {
                    setInStreamAssistantAction((prev) => {
                        if (prev) {
                            // console.log('setInStreamAssistantAction UNSETTING');
                            return null;
                        }
                    });
                }

                setInStreamAssistantMessage({ ...newAssistantMessage, content: streamText });
            },
            onFinish: async (streamText) => {
                // console.log('Stream finished:', streamText);
                const newConversation = await API.getConversation(selectedConversation);
                setInStreamAssistantMessage(null);
                setSelectedConversationMessages(newConversation.messages);
            },
            onError: (event) => {
                console.log('event.data', event.data);
                if (event.data && event.data.includes('OpenAI API')) {
                    addToast('warning', 'No OPENAI_API_KEY secret provided. Please add in the left bottom corner under Settings menu.');
                    // setInStreamAssistantMessage(null);
                }
                console.error('Stream error:', event);
            },
        });
        streamHandler.start();
    };

    const handleDeleteMessage = async (messageId) => {
        console.log('delete message', messageId);
        await API.deleteMessage(messageId);
        // refresh messages
        let fetchedConversation = await API.getConversation(selectedConversation);
        setSelectedConversationMessages(fetchedConversation.messages);
    };

    const handleEditMessage = async (messageId, content) => {
        console.log('edit message', messageId);
        await API.updateMessage(messageId, content);
        // refresh messages
        let fetchedConversation = await API.getConversation(selectedConversation);
        setSelectedConversationMessages(fetchedConversation.messages);
    };

    const handleRegenerateMessage = async (messageId) => {
        await handleDeleteMessage(messageId);
        await getAssistantResponse(selectedConversation);
    };

    const isLastAssistantMessage = (messageId) => {
        if (selectedConversationMessages.length === 0) return false;
        const lastMessage = selectedConversationMessages[selectedConversationMessages.length - 1];
        return lastMessage.sender === 'assistant' && lastMessage.id === messageId;
    };

    const handleUpsertConversationEmbeddings = async (conversationId) => {
        console.log('upsert conversation embeddings', conversationId);
        await API.upsertEmbeddings(conversationId);
        const fetchedConversations = (await API.getConversations()).reverse();
        setConversations(fetchedConversations);
    };

    const handleDeleteConversationEmbeddings = async (conversationId) => {
        console.log('delete conversation embeddings', conversationId);
        await API.deleteEmbeddings(conversationId);
        const fetchedConversations = (await API.getConversations()).reverse();
        setConversations(fetchedConversations);
    };

    const handleToolZipDrop = async (zipFiles) => {
        console.log('zipFiles:', zipFiles);
        try {
            const response = await API.uploadZipFile(zipFiles[0]);
            console.log('File upload response:', response);
            console.log('Refreshing the toolset...');
            const fetchedTools = await API.getTools();
            setTools(fetchedTools);
            // refresh the secrets
            const fetchedSecrets = await API.getSecrets();
            setSecrets(fetchedSecrets);
            return response;
        } catch (error) {
            console.error('File upload error:', error);
            return error;
        }
    };

    const getOpenAiToken = () => {
        const openAiToken = secrets.find((secret) => secret.name === 'OPENAI_API_KEY');
        return openAiToken;
    };

    const value = {
        MODELS: MODELS,
        selectedModel,
        setSelectedModel,
        conversations,
        tools,
        secrets,
        toggleTool,
        handleDeleteTool,
        setConversations,
        selectedConversation,
        setSelectedConversation,
        messages: selectedConversationMessages,
        setMessages: setSelectedConversationMessages,
        conversationLoading,
        setConversationLoading,
        inStreamAssistantMessage,
        setInStreamAssistantMessage,
        inStreamAssistantAction,
        setInStreamAssistantAction,
        handleToolZipDrop,
        handleAddNewConversation,
        handleDeleteConversation,
        handleChangeConversationTitle,
        handleSendMessage,
        handleDeleteMessage,
        handleEditMessage,
        handleRegenerateMessage,
        handleUpsertConversationEmbeddings,
        handleDeleteConversationEmbeddings,
        handleAddNewSecret,
        handleDeleteSecret,
        handleUpdateSecret,
        isLastAssistantMessage,
        toasts,
        addToast,
        removeToast,
        getOpenAiToken,
    };

    return <ConversationsContext.Provider value={value}>{children}</ConversationsContext.Provider>;
}
