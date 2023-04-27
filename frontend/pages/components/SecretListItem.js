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
        // <Box key={secret.id} display="flex" flexDirection="row" gap="0.5rem">
        <Box
            key={secret.id}
            sx={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                marginRight: '1rem',
                gap: '0.5rem',
            }}
        >
            <TextField
                key={secret.id}
                size="small"
                label={secret.key}
                sx={
                    {
                        // flexGrow: 12,
                    }
                }
                fullWidth
                disabled={!isEditing}
                value={isEditing ? editedValue : secret.value}
                onChange={(e) => setEditedValue(e.target.value)}
                InputProps={{
                    sx: { fontSize: '0.8rem', padding: 0 },
                    type: !isEditing ? (secret.value === 'TO_BE_PROVIDED' ? 'text' : 'password') : 'text',
                }}
                InputLabelProps={{ sx: { fontSize: '0.8rem' } }}
            />
            {isEditing || isDeleting ? (
                <>
                    <IconButton
                        sx={{
                            fontSize: '0.8rem',
                        }}
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
                        <DoneIcon fontSize="inherit" />
                    </IconButton>
                    <IconButton
                        edge="end"
                        color="inherit"
                        sx={{
                            fontSize: '0.8rem',
                        }}
                        onClick={() => (isEditing ? setIsEditing(false) : setIsDeleting(false))}
                    >
                        <CancelIcon fontSize="inherit" />
                    </IconButton>
                </>
            ) : (
                <>
                    <IconButton
                        // size="small"
                        edge="end"
                        color="inherit"
                        sx={{
                            fontSize: '0.8rem',
                        }}
                        onClick={() => setIsEditing(true)}
                    >
                        <EditIcon fontSize="inherit" />
                    </IconButton>
                    <IconButton
                        // size="small"
                        edge="end"
                        color="inherit"
                        sx={{
                            fontSize: '0.8rem',
                        }}
                        onClick={() => setIsDeleting(true)}
                    >
                        <DeleteIcon fontSize="inherit" />
                    </IconButton>
                </>
            )}
        </Box>
    );
}
