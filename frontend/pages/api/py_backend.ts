import axios, { AxiosResponse } from 'axios';
import { Conversation, Message, Role } from '../types';
const API_URL = process.env.NEXT_PUBLIC_PY_BACKEND_API_URL;

console.log('API_URL', API_URL);

export async function getConversationsWithMessages(): Promise<Conversation[]> {
    const response: AxiosResponse<Conversation[]> = await axios.get(`${API_URL}/conversations_with_messages`);
    return response.data;
}

export async function getConversations(): Promise<{ id: string; title: string }[]> {
    const response: AxiosResponse<{ id: string; title: string }[]> = await axios.get(`${API_URL}/conversations`);
    return response.data;
}

export async function createConversation(title: string, model?: string): Promise<Conversation> {
    const response: AxiosResponse<Conversation> = await axios.post(`${API_URL}/conversations`, { title, model });
    return response.data;
}

export async function getConversation(conversationId: string): Promise<{ id: string; title: string; messages: Message[] }> {
    const response: AxiosResponse<{ id: string; title: string; messages: Message[] }> = await axios.get(`${API_URL}/conversations/${conversationId}`);
    return response.data;
}

export async function updateConversation(conversationId: string, title: string): Promise<void> {
    await axios.put(`${API_URL}/conversations/${conversationId}`, { title });
}

export async function deleteConversation(conversationId: string): Promise<void> {
    await axios.delete(`${API_URL}/conversations/${conversationId}`);
}

export async function createMessage(conversationId: string, sender: Role, content: string, timestamp: string): Promise<Message> {
    const response: AxiosResponse<{ id: string }> = await axios.post(`${API_URL}/conversations/${conversationId}/messages`, {
        sender,
        content,
        timestamp,
    });
    return {
        id: response.data.id,
        sender,
        content,
        timestamp,
    };
}

export async function updateMessage(messageId: string, content: string): Promise<void> {
    await axios.put(`${API_URL}/messages/${messageId}`, { content });
}

export async function deleteMessage(messageId: string): Promise<void> {
    await axios.delete(`${API_URL}/messages/${messageId}`);
}

const API = {
    getConversations,
    createConversation,
    getConversation,
    updateConversation,
    deleteConversation,
    createMessage,
    updateMessage,
    deleteMessage,
};

export default API;
