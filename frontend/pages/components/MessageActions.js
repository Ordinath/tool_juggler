import { useState } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import DoneIcon from '@mui/icons-material/Done';
import CancelIcon from '@mui/icons-material/Cancel';
import { useConversations } from './ConversationsContext';

const MessageActions = ({ message, onEnableEdit }) => {
    const { handleDeleteMessage } = useConversations();

    const [confirmDelete, setConfirmDelete] = useState(false);

    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'flex-end',
                fontSize: '1.25rem',
                position: 'absolute',
                right: 5,
                top: 5,
                zIndex: 1,
            }}
        >
            {confirmDelete && (
                <>
                    <IconButton
                        size="small"
                        onClick={() => {
                            console.log(`Delete message ${message.id}`);
                            handleDeleteMessage(message.id);
                            setConfirmDelete(false);
                        }}
                    >
                        <DoneIcon fontSize="inherit" />
                    </IconButton>
                    <IconButton
                        size="small"
                        onClick={() => {
                            setConfirmDelete(false);
                        }}
                    >
                        <CancelIcon fontSize="inherit" />
                    </IconButton>
                </>
            )}
            {!confirmDelete && (
                <>
                    {message.sender === 'assistant' && (
                        <IconButton
                            size="small"
                            onClick={() => {
                                console.log(`Regenerate message ${message.id}`);
                            }}
                        >
                            <RefreshIcon fontSize="inherit" />
                        </IconButton>
                    )}
                    <IconButton
                        size="small"
                        onClick={() => {
                            console.log(`Edit message ${message.id}}`);
                        }}
                    >
                        <EditIcon fontSize="inherit" />
                    </IconButton>
                    <IconButton
                        size="small"
                        onClick={() => {
                            setConfirmDelete(true);
                        }}
                    >
                        <DeleteIcon fontSize="inherit" />
                    </IconButton>
                </>
            )}
        </Box>
    );
};

export default MessageActions;
