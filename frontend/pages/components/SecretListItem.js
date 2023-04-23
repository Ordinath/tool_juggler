import { useState } from 'react';

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';

import EditIcon from '@mui/icons-material/Edit';
import DoneIcon from '@mui/icons-material/Done';
import CancelIcon from '@mui/icons-material/Cancel';
import DeleteIcon from '@mui/icons-material/Delete';
import { useConversations } from './ConversationsContext';

export default function SecretListItem({ secret, index }) {
    const [isEditing, setIsEditing] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [editedValue, setEditedValue] = useState(secret.value);
    const { handleUpdateSecret, handleDeleteSecret } = useConversations();

    return (
        <Box key={secret.id}>
            <Box display="flex" flexDirection="column" gap="0.5rem">
                <TextField
                    size="small" 
                    label="Key" 
                    value={secret.key} 
                    disabled 
                    InputProps={{ style: { fontSize: '0.7rem' } }} 
                />
                <TextField
                    size="small"
                    label="Value"
                    disabled={!isEditing}
                    value={isEditing ? editedValue : secret.value}
                    onChange={(e) => setEditedValue(e.target.value)}
                    InputProps={{ style: { fontSize: '0.7rem' } }}
                />
                <Box display="flex" flexDirection="row" gap="0.5rem">
                    {isEditing || isDeleting ? (
                        <>
                            <IconButton
                                edge="end"
                                color="inherit"
                                onClick={() => {
                                    if (isEditing) {
                                        handleUpdateSecret(secret.id, secret.key, editedValue);
                                        setIsEditing(false);
                                    } else if (isDeleting) {
                                        handleDeleteSecret(secret.id);
                                        setIsDeleting(false);
                                    }
                                }}
                            >
                                <DoneIcon />
                            </IconButton>
                            <IconButton edge="end" color="inherit" onClick={() => (isEditing ? setIsEditing(false) : setIsDeleting(false))}>
                                <CancelIcon />
                            </IconButton>
                        </>
                    ) : (
                        <>
                            <IconButton edge="end" color="inherit" onClick={() => setIsEditing(true)}>
                                <EditIcon />
                            </IconButton>
                            <IconButton edge="end" color="inherit" onClick={() => setIsDeleting(true)}>
                                <DeleteIcon />
                            </IconButton>
                        </>
                    )}
                </Box>
            </Box>
        </Box>
    );
}
