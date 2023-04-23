import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Collapse from '@mui/material/Collapse';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowDropUpIcon from '@mui/icons-material/ArrowDropUp';
import { useState } from 'react';
import Typography from '@mui/material/Typography';
import SecretsList from './SecretsList';

export default function Settings() {
    const [collapsed, setCollapsed] = useState(true);

    return (
        <Box
            display="flex"
            flexDirection="column"
            // gap="0.5rem"
            width="100%"
            sx={{ overflowY: 'scroll', fontSize: '0.8rem', alignSelf: 'flex-end', width: '100%' }}
        >
            <Button
                // variant='text'
                disableRipple
                disableFocusRipple
                disableTouchRipple
                onClick={() => setCollapsed(!collapsed)}
                sx={{
                    borderTop: '2px solid #e0e0e0',
                    borderRadius: 0,
                    marginTop: '1rem',
                    justifyContent: 'center',
                    '&:hover': {
                        backgroundColor: 'transparent',
                        fontWeight: 'bold',
                    },
                }}
            >
                <Typography variant="h6" fontWeight="inherit">
                    Settings
                </Typography>{' '}
                {collapsed ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
            </Button>
            <Collapse in={!collapsed}>
                <SecretsList />
            </Collapse>
        </Box>
    );

    // return (
    //     <Box display="flex" flexDirection="column" gap="1rem" width="100%" sx={{ overflowY: 'scroll' }}>
    //         <Button variant="outlined" fullWidth onClick={() => setCollapsed(!collapsed)}>
    //             Secrets
    //         </Button>
    //         <Collapse in={!collapsed}>
    //             {secrets.map((secret) => (
    //                 <Box display="flex" flexDirection="row" gap="1rem" alignItems="center" key={secret.id}>
    //                     <TextField label="Key" value={secret.key} disabled />
    //                     <TextField label="Value" value={secret.value} onChange={(e) => handleUpdateSecret(secret.id, secret.key, e.target.value)} />
    //                     <IconButton
    //                         edge="end"
    //                         color="inherit"
    //                         onClick={() => {
    //                             handleDeleteSecret(secret.id);
    //                         }}
    //                     >
    //                         <DeleteIcon />
    //                     </IconButton>
    //                 </Box>
    //             ))}
    //             <Box display="flex" flexDirection="row" gap="1rem" alignItems="center">
    //                 <TextField label="New Key" value={newSecretKey} onChange={(e) => setNewSecretKey(e.target.value)} />
    //                 <TextField label="New Value" value={newSecretValue} onChange={(e) => setNewSecretValue(e.target.value)} />
    //                 <IconButton
    //                     edge="end"
    //                     color="inherit"
    //                     onClick={() => {
    //                         handleAddNewSecret(newSecretKey, newSecretValue);
    //                         setNewSecretKey('');
    //                         setNewSecretValue('');
    //                     }}
    //                 >
    //                     <AddIcon />
    //                 </IconButton>
    //             </Box>
    //         </Collapse>
    //     </Box>
    // );
}
