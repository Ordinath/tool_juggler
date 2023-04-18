import { log } from 'console';
import { SSE } from '../lib/sse';

export interface StreamHandlerOptions {
    apiKey?: string;
    endpoint: string;
    model?: string;
    assistant_message_id: string;
    // messages: { role: string; content: string }[];
    onMessage: (msg: string, streamText: string) => void;
    onError: (err: Error) => void;
    onFinish: (streamText: string) => void;
}

export class StreamHandler {
    private options: StreamHandlerOptions;
    private eventSource: any = null;
    public streamText: string = '';

    constructor(options: StreamHandlerOptions) {
        this.options = options;
    }

    public start() {
        console.log('start');
        console.log('options', this.options);
        if (this.eventSource) {
            throw new Error('Stream already started');
        }

        const request = {
            method: 'POST',
            headers: {
                Authorization: this.options.apiKey ? `Bearer ${this.options.apiKey}` : undefined,
                'Content-Type': 'application/json',
            },
            payload: JSON.stringify({
                // messages: this.options.messages,
                model: this.options.model ? this.options.model : undefined,
                assistant_message_id: this.options.assistant_message_id,
                stream: true,
            }),
        };

        this.eventSource = new SSE(this.options.endpoint, request);
        this.eventSource.addEventListener('message', this.handleMessage.bind(this));
        this.eventSource.addEventListener('error', this.handleError.bind(this));

        this.eventSource.stream();
    }

    public stop() {
        console.log('stop');
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }

    private handleMessage(event: MessageEvent) {
        const text = decodeURIComponent(event.data);
        if (text === '[DONE]') {
            this.options.onFinish(this.streamText);
            this.stop();
            return;
        }
        if (text !== undefined) {
            // if text matches the /\[\[(.*?)\]\]/ regex, we dont want to add it to the streamText
            // made to track AI assistant action messages
            const regex = /\[\[(.*?)\]\]/;
            const match = text.match(regex);
            if (match) {
                console.log('AI assistant action', match[1]);
            } else {
                this.streamText += text;
            }

            // if (!regex.test(text)) {
            //     console.log('text', text);
            //     this.streamText += text;
            // }
            this.options.onMessage(text, this.streamText);
        }
    }

    private handleError(event: Event) {
        const err = new Error('Error during streaming');
        this.options.onError(err);
        this.stop();
    }
}
