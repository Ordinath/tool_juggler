export type Role = 'user' | 'assistant' | 'system';

export type Ccm = {
    role: Role;
    content: string;
};

export type Message = {
    id?: string;
    sender: Role;
    content: string;
    timestamp: string;
};

export type Conversation = {
    id: string;
    title: string;
    messages?: Message[];
    model?: string;
};