import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import IconButton from '@mui/material/IconButton';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Tooltip from '@mui/material/Tooltip';
import GraphicEqIcon from '@mui/icons-material/GraphicEq';
import { useEffect, useState, useRef } from 'react';
import { useConversations } from './ConversationsContext';

const WHISPER_PROMPT =
    'This transcription might contain topics, adjacent and related to ERP/CRM/iPaaS/SaaS technologies, project management in distributed software systems and might include references to NetSuite, Salesforce, Workato, Celigo, AWS, JIRA, SuiteScript, JavaScript and other related to this terminology words. Additionally, it might contain not only English but other languages as Russian, German, etc. It might also include references to services for solar panels and other electrical equipment installations in Titan Solar Power AZ and other US States. It might reference javascript, python frontend and backend technologies and frameworks, REST requests etc';
const TRANSCRIPTION_URL = 'https://api.openai.com/v1/audio/transcriptions';

export default function UserInput() {
    const { handleSendMessage, getOpenAiToken } = useConversations();
    const [userMessage, setUserMessage] = useState('');
    const inputRef = useRef(null);

    // audio recorder stuff
    const [recordingStatus, setRecordingStatus] = useState('inactive'); // inactive, recording, processing
    const [mediaRecorder, setMediaRecorder] = useState(null);

    const insertTextResult = (text) => {
        const input = inputRef.current;
        const start = input.selectionStart;
        const end = input.selectionEnd;

        const newValue = userMessage.substring(0, start) + text + userMessage.substring(end);

        setUserMessage(newValue);
    };

    useEffect(() => {
        const processRecording = async (chunks, stream) => {
            setRecordingStatus('processing');
            const audioBlob = new Blob(chunks, { type: 'audio/webm' });
            const file = audioBlob;
            // const token = process.env.NEXT_PUBLIC_OPENAI_API_KEY;
            const token = getOpenAiToken();
            const headers = new Headers({
                Authorization: `Bearer ${token}`,
            });
            const formData = new FormData();
            formData.append('file', file, 'recording.webm');
            formData.append('model', 'whisper-1');
            formData.append('prompt', WHISPER_PROMPT);
            const requestOptions = {
                method: 'POST',
                headers,
                body: formData,
                redirect: 'follow',
            };
            const requestUrl = TRANSCRIPTION_URL;
            const response = await fetch(requestUrl, requestOptions);
            setRecordingStatus('inactive');
            if (response.status === 200) {
                const result = await response.json();
                const resultText = result.text;
                console.log(resultText);

                insertTextResult(resultText);
                // this.recording = false;
                stream.getTracks().forEach((track) => track.stop());
            } else {
                insertTextResult(
                    `${response.status} ERROR! API key not provided or OpenAI Server Error! Check the Settings to provide API key.`
                );
                // this.recording = false;
                stream.getTracks().forEach((track) => track.stop());
            }
        };

        const startRecording = async () => {
            console.log('start recording');
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const newMediaRecorder = new MediaRecorder(stream);
            let chunks = [];
            newMediaRecorder.addEventListener('dataavailable', (event) => chunks.push(event.data));
            newMediaRecorder.addEventListener('stop', (event) => processRecording(chunks, stream));
            newMediaRecorder.start();
            setMediaRecorder(newMediaRecorder);
        };

        const stopRecording = async () => {
            console.log('stop recording');
            await mediaRecorder.stop();
            setMediaRecorder(null);
        };

        if (recordingStatus === 'recording') {
            startRecording();
        } else if (recordingStatus === 'processing') {
            stopRecording();
        }
    }, [recordingStatus]);

    return (
        <Box className="message-input" sx={{ alignSelf: 'flex-end', width: '100%' }}>
            <Grid container spacing={1} alignItems="flex-end">
                <Grid item xs={12}>
                    <OutlinedInput
                        fullWidth
                        inputRef={inputRef}
                        onChange={(e) => setUserMessage(e.target.value)}
                        value={userMessage}
                        size="small"
                        multiline
                        minRows={1}
                        maxRows={10}
                        // upon pressing cmd+enter, send message
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && e.metaKey) {
                                handleSendMessage(userMessage);
                                setUserMessage('');
                            }
                            if (e.key === 'r' && e.ctrlKey) {
                                e.preventDefault(); // prevent the default behavior of the Ctrl+R combination
                                if (recordingStatus === 'inactive') {
                                    setRecordingStatus('recording');
                                } else if (recordingStatus === 'recording') {
                                    setRecordingStatus('processing');
                                }
                            }
                        }}
                        sx={{
                            paddingY: '0.7rem',
                            paddingRight: '4rem',
                        }}
                        endAdornment={
                            <InputAdornment position="end">
                            <Tooltip title="Cmd+Enter to send" enterDelay={500}>
                                
                                <IconButton
                                    edge="end"
                                    color="inherit"
                                    aria-label="send message"
                                    onClick={() => {
                                        // Handle send button click
                                        handleSendMessage(userMessage);
                                        setUserMessage('');
                                    }}
                                    sx={{
                                        position: 'absolute',
                                        bottom: 5.5,
                                        right: 15,
                                    }}
                                >
                                    <SendIcon fontSize="small" />
                                </IconButton>
                            </Tooltip>
                                <Tooltip title="Ctrl+R to start/stop recording" enterDelay={500}>
                                    <IconButton
                                        edge="end"
                                        color="inherit"
                                        aria-label="record audio"
                                        onClick={() => {
                                            // Handle microphone button click
                                            if (recordingStatus === 'inactive') {
                                                setRecordingStatus('recording');
                                            } else if (recordingStatus === 'recording') {
                                                setRecordingStatus('processing');
                                            }
                                        }}
                                        disabled={recordingStatus === 'processing'}
                                        sx={{
                                            position: 'absolute',
                                            bottom: 5.5,
                                            right: 55,
                                        }}
                                    >
                                        {recordingStatus === 'inactive' && <MicIcon fontSize="small" />}
                                        {recordingStatus === 'recording' && <GraphicEqIcon color="primary" className="squeeze" fontSize="small" />}
                                        {recordingStatus === 'processing' && <CircularProgress color="primary" size={20} />}
                                    </IconButton>
                                </Tooltip>
                            </InputAdornment>
                        }
                    />
                </Grid>
            </Grid>
        </Box>
    );
}
