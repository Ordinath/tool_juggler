import axios, { AxiosResponse } from 'axios';
import { Conversation, Message, Role, Tool, Secret } from '../types';
// const API_URL = process.env.NEXT_PUBLIC_PY_BACKEND_API_URL;
import { API_URL } from '../constants';

console.log('API_URL', API_URL);

export async function getConversationsWithMessages(): Promise<Conversation[]> {
    const response: AxiosResponse<Conversation[]> = await axios.get(`${API_URL}/conversations_with_messages`);
    return response.data;
}

export async function getConversations(): Promise<{ id: string; title: string; embedded: boolean }[]> {
    const response: AxiosResponse<{ id: string; title: string; embedded: boolean }[]> = await axios.get(`${API_URL}/conversations`);
    return response.data;
}

export async function createConversation(title: string, model?: string): Promise<Conversation> {
    const response: AxiosResponse<Conversation> = await axios.post(`${API_URL}/conversations`, { title, model });
    return response.data;
}

export async function getConversation(conversationId: string): Promise<{ id: string; title: string; embedded: boolean; messages: Message[] }> {
    const response: AxiosResponse<{ id: string; title: string; embedded: boolean; messages: Message[] }> = await axios.get(
        `${API_URL}/conversations/${conversationId}`
    );
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

export async function upsertEmbeddings(conversationId: string): Promise<{ id: string }> {
    const response: AxiosResponse<{ id: string }> = await axios.post(`${API_URL}/conversations/${conversationId}/upsert_long_term_memory_embedding`);
    return response.data;
}

export async function deleteEmbeddings(conversationId: string): Promise<void> {
    await axios.delete(`${API_URL}/conversations/${conversationId}/delete_long_term_memory_embedding`);
}

export async function uploadZipFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('upload_file', file);
    const response: AxiosResponse<any> = await axios.post(`${API_URL}/upload_tool_zip`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
}

export async function getTools(): Promise<Tool[]> {
    const response: AxiosResponse<Tool[]> = await axios.get(`${API_URL}/tools`);
    return response.data;
}

export async function toggleTool(toolId: string, enabled: boolean): Promise<void> {
    await axios.put(`${API_URL}/tools/${toolId}/toggle`, { enabled: !enabled });
}

export async function deleteTool(toolId: string): Promise<void> {
    await axios.delete(`${API_URL}/tools/${toolId}`);
}

// Get all secrets
export async function getSecrets(): Promise<Secret[]> {
    const response: AxiosResponse<Secret[]> = await axios.get(`${API_URL}/secrets`);
    // console.log('get Secrets response.data', response.data);
    return response.data;
}

// Get secret by ID
export async function getSecret(secretId: string): Promise<Secret> {
    const response: AxiosResponse<Secret> = await axios.get(`${API_URL}/secrets/${secretId}`);
    return response.data;
}

// Create secret
export async function createSecret(key: string, value: string): Promise<Secret> {
    const response: AxiosResponse<Secret> = await axios.post(`${API_URL}/secrets`, { key, value });
    return response.data;
}

// Update secret
export async function updateSecret(secretId: string, key: string, value: string): Promise<Secret> {
    const response: AxiosResponse<Secret> = await axios.put(`${API_URL}/secrets/${secretId}`, { key, value });
    return response.data;
}

// Delete secret
export async function deleteSecret(secretId: string): Promise<void> {
    await axios.delete(`${API_URL}/secrets/${secretId}`);
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
    upsertEmbeddings,
    deleteEmbeddings,
    uploadZipFile,
    getTools,
    toggleTool,
    deleteTool,
    getSecrets,
    getSecret,
    createSecret,
    updateSecret,
    deleteSecret,
};

export default API;
