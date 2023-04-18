import { useState } from 'react';
import { styled, alpha } from '@mui/material/styles';
import Box from '@mui/material/Box';
import { IconButton } from '@mui/material';
import FileCopyIcon from '@mui/icons-material/FileCopyOutlined';
import ReactMarkdown from 'react-markdown';
import OutlinedInput from '@mui/material/OutlinedInput';
import MessageActions from './MessageActions';
import BlinkingDots from './BlinkingDots';
import { useConversations } from './ConversationsContext';
// import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MessageBox = styled(Box)(({ hascontent, theme }) => ({
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    // padding: theme.spacing(3),
    marginBottom: theme.spacing(1),
    paddingLeft: theme.spacing(2.5),
    paddingRight: theme.spacing(2.5),
    paddingTop: theme.spacing(2),
    paddingBottom: hascontent === 'true' ? theme.spacing(0) : theme.spacing(3),
    wordBreak: 'break-word',
    wordWrap: 'break-word',
}));
const StreamedActionBox = styled(Box)(({ theme }) => ({
    paddingTop: theme.spacing(2),
}));

const EditBox = styled(OutlinedInput)(({ editmode, selected, confirmdelete, theme }) => ({
    '& .MuiInputBase-input.Mui-disabled': {
        WebkitTextFillColor: undefined,
    },
    paddingTop: theme.spacing(2),
}));

const SystemMessage = styled(MessageBox)(({ theme }) => ({
    background: alpha(theme.palette.info.dark, 0.3),
    border: `1px solid ${theme.palette.info.main}`,
}));

const UserMessage = styled(MessageBox)(({ hascontent, theme }) => ({
    background: alpha(theme.palette.primary.dark, 0.3),
    border: `1px solid ${alpha(theme.palette.secondary.main, 0.9)}`,
}));

const AssistantMessage = styled(MessageBox)(({ hascontent, theme }) => ({
    background: alpha(theme.palette.secondary.dark, 0.3),
    border: `1px solid ${alpha(theme.palette.primary.main, 0.9)}`,
}));

const renderedComponents = {
    code({ node, ...props }) {
        return !props.inline ? (
            // <div style={{ position: 'relative', display: 'inline-block', backgroundColor: 'rgba(0, 0, 0, 0.2)', padding: 10, width: '100%' }}>
            <div
                style={{
                    position: 'relative',
                    display: 'inline-block',
                    width: '100%',
                    maxWidth: '100%',
                    backgroundColor: 'rgba(0, 0, 0, 0.2)',
                    padding: '1.5rem',
                    fontSize: '.875rem',
                    wordBreak: 'break-word',
                    wordWrap: 'break-word',
                }}
            >
                <code
                    {...props}
                    style={{
                        wordBreak: 'break-word',
                        wordWrap: 'break-word',
                    }}
                />
                {/* <SyntaxHighlighter language={node.properties.className?.[0].split('-')[1]} style={oneDark}>
                    {props.children[0]}
                </SyntaxHighlighter> */}
                <IconButton
                    size="small"
                    style={{
                        position: 'absolute',
                        top: 6,
                        right: 2,
                        color: 'white',
                        zIndex: 1,
                    }}
                    onClick={() => handleCopyToClipboard(props.children)}
                >
                    <FileCopyIcon />
                </IconButton>
            </div>
        ) : (
            <div style={{ position: 'relative', display: 'inline-block', backgroundColor: 'rgba(0, 0, 0, 0.2)', padding: '2px 5px' }}>
                <code {...props} />
            </div>
        );
    },
};

const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(
        () => {
            console.log('Text copied to clipboard');
        },
        (err) => {
            console.error('Error copying text to clipboard:', err);
        }
    );
};

export default function Message({ message, streamedAction }) {
    const messageTextStyle = { wordWrap: 'break-word', overflowWrap: 'break-word' };

    const { handleEditMessage } = useConversations();

    // track the state of message edit status and message edit content
    const [isEditing, setIsEditing] = useState(false);
    const [editContent, setEditContent] = useState(message.content);

    const handleMessageEnableEdit = () => {
        setIsEditing(true);
    };

    const handleMessageEditConfirm = () => {
        setIsEditing(false);
        handleEditMessage(message.id, editContent);
    };

    const handleMessageEditCancel = () => {
        setIsEditing(false);
    };

    return (
        <Box key={message.id}>
            {/* {message.sender === 'system' && (
                <SystemMessage className="system-message" width="100%">
                    <ReactMarkdown style={messageTextStyle} children={message.content} components={renderedComponents} />
                </SystemMessage>
            )} */}
            {message.sender === 'user' && (
                <UserMessage className="user-message" width="100%" hascontent={`${message.content.trim().length !== 0}`}>
                    <MessageActions
                        message={message}
                        onEnableEdit={handleMessageEnableEdit}
                        isEditing={isEditing}
                        onConfirmEdit={handleMessageEditConfirm}
                        onCancelEdit={handleMessageEditCancel}
                    />
                    {isEditing ? (
                        <>
                            <EditBox
                                fullWidth
                                multiline
                                onChange={(e) => {
                                    setEditContent(e.target.value);
                                }}
                                value={editContent}
                                sx={{
                                    '& fieldset': { border: 'none' },
                                    paddingX: 0,
                                }}
                            />
                        </>
                    ) : (
                        <ReactMarkdown style={messageTextStyle} children={message.content} components={renderedComponents} />
                    )}
                </UserMessage>
            )}
            {message.sender === 'assistant' && (
                <AssistantMessage className="assistant-message" width="100%" hascontent={`${message.content.trim().length !== 0}`}>
                    <MessageActions
                        message={message}
                        onEnableEdit={handleMessageEnableEdit}
                        isEditing={isEditing}
                        onConfirmEdit={handleMessageEditConfirm}
                        onCancelEdit={handleMessageEditCancel}
                    />
                    {isEditing ? (
                        <>
                            <EditBox
                                fullWidth
                                multiline
                                onChange={(e) => {
                                    setEditContent(e.target.value);
                                }}
                                value={editContent}
                                sx={{
                                    '& fieldset': { border: 'none' },
                                    paddingX: 0,
                                }}
                            />
                        </>
                    ) : streamedAction ? (
                        <StreamedActionBox>
                            <BlinkingDots>Tool Juggler is using {streamedAction} tool</BlinkingDots>
                        </StreamedActionBox>
                    ) : (
                        <ReactMarkdown style={messageTextStyle} children={message.content} components={renderedComponents} />
                    )}
                </AssistantMessage>
            )}
        </Box>
    );
}
