import { useState } from 'react';

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import SecretListItem from './SecretListItem';

import AddIcon from '@mui/icons-material/Add';
import { useConversations } from './ConversationsContext';
import { Typography } from '@mui/material';

export default function SecretsList() {
    const { secrets, handleAddNewSecret } = useConversations();

    const [newSecretKey, setNewSecretKey] = useState('');
    const [newSecretValue, setNewSecretValue] = useState('');

    return (
        <Box display="flex" flexDirection="column" gap="0.5rem" width="100%">
            <Typography>Secrets</Typography>
            {secrets && secrets.map((secret, index) => <SecretListItem key={secret.id} secret={secret} index={index} />)}
            <Box
                sx={{
                    borderTop: '1px solid #e0e0e0',
                    paddingTop: '0.5rem',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    marginRight: '1rem',
                    gap: '0.5rem',
                }}
            >
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: 'center',
                        marginRight: '1rem',
                        gap: '0.5rem',
                    }}
                >
                    <TextField
                        size="small"
                        label="New Key"
                        fullWidth
                        value={newSecretKey}
                        onChange={(e) => setNewSecretKey(e.target.value)}
                        InputProps={{ style: { fontSize: '0.8rem' } }}
                        InputLabelProps={{ sx: { fontSize: '0.8rem' } }}
                    />
                    <TextField
                        size="small"
                        label="New Value"
                        value={newSecretValue}
                        fullWidth
                        onChange={(e) => setNewSecretValue(e.target.value)}
                        InputProps={{ style: { fontSize: '0.8rem' } }}
                        InputLabelProps={{ sx: { fontSize: '0.8rem' } }}
                    />
                    <Box>
                        <IconButton
                            edge="end"
                            color="inherit"
                            sx={{
                                fontSize: '0.8rem',
                            }}
                            onClick={() => {
                                handleAddNewSecret(newSecretKey, newSecretValue);
                                setNewSecretKey('');
                                setNewSecretValue('');
                            }}
                        >
                            <AddIcon fontSize="inherit" />
                        </IconButton>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
}
