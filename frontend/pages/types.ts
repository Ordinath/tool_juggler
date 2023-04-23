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

export type Tool = {
    id: string;
    name: string;
    enabled: boolean;
    core: boolean;
    tool_type: string;
    manifest: Record<string, any>;
    description: string;
    created_at: string;
    updated_at: string | null;
};

export interface Secret {
    id: string;
    key: string;
    value?: string;
}