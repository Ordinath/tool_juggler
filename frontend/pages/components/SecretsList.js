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
            <Box display="flex" flexDirection="column" gap="0.5rem" alignItems="flex-start">
                <TextField
                    size="small"
                    label="New Key"
                    value={newSecretKey}
                    onChange={(e) => setNewSecretKey(e.target.value)}
                    // InputProps={{ style: { fontSize: '0.8rem' } }}
                />
                <TextField
                    size="small"
                    label="New Value"
                    value={newSecretValue}
                    onChange={(e) => setNewSecretValue(e.target.value)}
                    // InputProps={{ style: { fontSize: '0.8rem' } }}
                />
                <Box mt={1}>
                    <IconButton
                        edge="end"
                        color="inherit"
                        onClick={() => {
                            handleAddNewSecret(newSecretKey, newSecretValue);
                            setNewSecretKey('');
                            setNewSecretValue('');
                        }}
                    >
                        <AddIcon />
                    </IconButton>
                </Box>
            </Box>
        </Box>
    );
}
