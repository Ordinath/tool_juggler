import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Collapse from '@mui/material/Collapse';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowDropUpIcon from '@mui/icons-material/ArrowDropUp';
import { useState } from 'react';
import Typography from '@mui/material/Typography';
import SecretsListSetting from './SecretsListSetting';
import ModelSetting from './ModelSetting';

export default function Settings() {
    const [collapsed, setCollapsed] = useState(true);

    return (
        <Box
            display="flex"
            flexDirection="column"
            // gap="0.5rem"
            width="100%"
            sx={{ fontSize: '0.8rem', alignSelf: 'flex-end', width: '100%', }}
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
                    // marginTop: '1rem',
                    justifyContent: 'center',
                    '&:hover': {
                        backgroundColor: 'transparent',
                        fontWeight: 'bold',
                    },
                    // '&::before': {
                    //     content: '""',
                    //     position: 'absolute',
                    //     top: 0,
                    //     left: 0,
                    //     width: '100%',
                    //     height: '10px',
                    //     background: 'linear-gradient(to top, #e0e0e0, transparent)',
                    // },
                }}
            >
                <Typography variant="h6" fontWeight="inherit">
                    Settings
                </Typography>{' '}
                {collapsed ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
            </Button>
            <Collapse in={!collapsed}>
                <Box
                    sx={{
                        overflowY: 'auto',
                    }}
                >
                    <ModelSetting />
                    <SecretsListSetting />
                </Box>
            </Collapse>
        </Box>
    );
}
