export default class AudioRecorder {
    constructor() {
        this.recording = false;
        this.mediaRecorder = null;
        // this.textarea = null;
        // this.micButton = null;
        this.token = null;
        // this.snippetButtons = [];
    }

    createMicButton() {
        this.micButton = document.createElement('button');
        this.micButton.className = `microphone_button ${MICROPHONE_BUTTON_CLASSES}`;
        this.micButton.style.marginRight = '2.2rem';
        this.micButton.innerHTML = SVG_MIC_HTML;
        this.micButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleRecording();
        });
    }

    async createSnippetButtons() {
        const snippets = await retrieveFromStorage('snippets');
        if (!snippets) return;

        const numberOfRows = Math.ceil(snippets.length / 9);
        // console.log(numberOfRows);
        snippets.forEach((snippet, index) => {
            if (!snippet) return;
            const button = document.createElement('button');
            button.textContent = index + 1;
            button.className = `snippet_button ${MICROPHONE_BUTTON_CLASSES}`;

            // we want to position the buttons in a grid
            // the grid is 9 columns wide and as many rows as needed
            const y = -0.6 - numberOfRows * 2.2 + Math.floor(index / 9) * 2.2;
            const x = -45.7 + (index % 9) * 2;
            button.style.transform = `translate(${x}rem, ${y}rem)`;

            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.insertTextResult(snippet);
            });
            this.textarea.parentNode.insertBefore(button, this.textarea.nextSibling);
            this.snippetButtons.push({ button, x, y, initialY: y });
        });
    }

    updateButtonGridPosition() {
        const textareaRows = this.textarea.clientHeight / 24;

        if (this.snippetButtons) {
            this.snippetButtons.forEach((buttonObj, index) => {
                buttonObj.y = buttonObj.initialY - (textareaRows - 1) * 1.5;
                buttonObj.button.style.transform = `translate(${buttonObj.x}rem, ${buttonObj.y}rem)`;
            });
        }
    }

    observeTextareaResize() {
        this.resizeObserver = new ResizeObserver(() => {
            // console.log('Textarea resized'); // Added console log
            this.updateButtonGridPosition();
        });
        this.resizeObserver.observe(this.textarea);
    }

    async downloadEnabled() {
        const downloadEnabled = await retrieveFromStorage('config_enable_download');
        // console.log('downloadEnabled', downloadEnabled);
        return downloadEnabled;
    }

    async translationEnabled() {
        const translationEnabled = await retrieveFromStorage('config_enable_translation');
        // console.log('translationEnabled', translationEnabled);
        return translationEnabled;
    }

    async snippetsEnabled() {
        const snippetsEnabled = await retrieveFromStorage('config_enable_snippets');
        // console.log('snippetsEnabled', snippetsEnabled);
        return snippetsEnabled;
    }

    async retrieveToken() {
        return await retrieveFromStorage('openai_token');
    }

    async getSelectedPrompt() {
        const selectedPrompt = await retrieveFromStorage('openai_selected_prompt');
        const prompts = await retrieveFromStorage('openai_prompts');
        // if (!prompts) we initialize the prompts (first time user)
        if (!prompts || !selectedPrompt) {
            // backwards compatibility with 1.0 version
            const previousVersionPrompt = await retrieveFromStorage('openai_prompt');

            const initialPrompt = {
                title: 'Initial prompt',
                content: previousVersionPrompt
                    ? previousVersionPrompt
                    : `The transcript is about OpenAI which makes technology like DALL·E, GPT-3, and ChatGPT with the hope of one day building an AGI system that benefits all of humanity.`,
            };
            await chrome.storage?.sync.set(
                {
                    openai_prompts: [initialPrompt],
                    openai_selected_prompt: 0,
                },
                () => {
                    // console.log('Config stored');
                }
            );
            return initialPrompt;
        } else {
            return prompts[selectedPrompt];
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            let chunks = [];
            this.mediaRecorder.addEventListener('dataavailable', (event) => chunks.push(event.data));

            this.mediaRecorder.addEventListener('stop', async () => {
                this.setButtonState('loading');
                console.log('recording stop');
                const audioBlob = new Blob(chunks, { type: 'audio/webm' });

                const file = audioBlob;

                if (await this.downloadEnabled()) {
                    downloadFile(file);
                }

                const storedToken = await this.retrieveToken();
                const storedPrompt = await this.getSelectedPrompt();
                console.log('storedPrompt', storedPrompt);

                const headers = new Headers({
                    Authorization: `Bearer ${storedToken}`,
                });
                const formData = new FormData();
                formData.append('file', file, 'recording.webm');
                formData.append('model', 'whisper-1');
                formData.append('prompt', storedPrompt.content);

                const requestOptions = {
                    method: 'POST',
                    headers,
                    body: formData,
                    redirect: 'follow',
                };

                const requestUrl = (await this.translationEnabled()) ? TRANSLATION_URL : TRANSCRIPTION_URL;

                const response = await fetch(requestUrl, requestOptions);
                this.setButtonState('ready');
                if (response.status === 200) {
                    const result = await response.json();
                    const resultText = result.text;
                    console.log(resultText);

                    this.insertTextResult(resultText);
                    this.recording = false;
                    stream.getTracks().forEach((track) => track.stop());
                } else {
                    this.insertTextResult(
                        `${response.status} ERROR! API key not provided or OpenAI Server Error! Check the Pop-up window of the Extension to provide API key.`
                    );
                    this.recording = false;
                    stream.getTracks().forEach((track) => track.stop());
                }
            });
            this.mediaRecorder.start();
            this.setButtonState('recording');
            this.recording = true;
        } catch (error) {
            console.error(error);
        }
    }

    stopRecording() {
        this.mediaRecorder.stop();
        this.micButton.innerHTML = SVG_MIC_HTML;
        this.recording = false;
    }

    toggleRecording() {
        if (!this.recording) {
            this.startRecording();
        } else {
            this.stopRecording();
        }
    }

    insertTextResult(resultText) {
        const startPos = this.textarea.selectionStart;
        const endPos = this.textarea.selectionEnd;
        const newText = this.textarea.value.substring(0, startPos) + resultText + this.textarea.value.substring(endPos);
        this.textarea.value = newText;
        this.textarea.selectionStart = startPos + resultText.length;
        this.textarea.selectionEnd = this.textarea.selectionStart;
        this.textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }

    setButtonState(state) {
        const hoverClasses = ['hover:bg-gray-100', 'dark:hover:text-gray-400', 'dark:hover:bg-gray-900'];
        switch (state) {
            case 'recording':
                this.micButton.disabled = false;
                this.micButton.innerHTML = SVG_MIC_SPINNING_HTML;
                break;
            case 'loading':
                this.micButton.disabled = true;
                this.micButton.innerHTML = SVG_SPINNER_HTML;
                this.micButton.classList.remove(...hoverClasses);
                break;
            case 'ready':
            default:
                this.micButton.disabled = false;
                this.micButton.innerHTML = SVG_MIC_HTML;
                this.micButton.classList.add(...hoverClasses);
                break;
        }
    }
}