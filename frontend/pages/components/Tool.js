import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { styled, alpha } from '@mui/material/styles';
import { useConversations } from './ConversationsContext';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import DoneIcon from '@mui/icons-material/Done';
import CancelIcon from '@mui/icons-material/Cancel';

const EnabledToolButton = styled(Button)(({ theme }) => ({
    backgroundColor: alpha(theme.palette.secondary.main, 0.3),
    color: '#fff',
    border: `.0875rem solid ${theme.palette.primary.main}`,
}));

const DisabledToolButton = styled(Button)(({ confirmdelete, theme }) => ({
    backgroundColor: confirmdelete === 'true' ? alpha(theme.palette.error.main, 0.3) : undefined,
    border: `.0875rem solid ${confirmdelete === 'true' ? alpha(theme.palette.error.main, 0.9) : undefined}`,
    color: confirmdelete === 'true' ? '#fff' : undefined,
    '&:hover': {
        backgroundColor: confirmdelete === 'true' ? alpha(theme.palette.error.main, 0.5) : alpha(theme.palette.secondary.main, 0.2),
        borderColor: confirmdelete === 'true' ? alpha(theme.palette.error.main, 0.5) : undefined,
        color: confirmdelete === 'true' ? '#fff' : undefined,
    },
}));

export default function Tool({ tool, onDelete }) {
    const { toggleTool, handleDeleteTool } = useConversations();
    const [confirmDelete, setConfirmDelete] = useState(false);

    return (
        <Box key={tool.id} width="100%" sx={{ position: 'relative', paddingLeft: '2rem' }}>
            {tool.enabled ? (
                <Box width="100%">
                    <EnabledToolButton
                        sx={{
                            paddingY: '0.375rem',
                            justifyContent: 'flex-end',
                        }}
                        disableRipple={true}
                        variant="outlined"
                        fullWidth
                        onClick={() => {
                            toggleTool(tool.id, tool.enabled);
                        }}
                    >
                        {tool.name}
                    </EnabledToolButton>
                </Box>
            ) : (
                <Box width="100%">
                    <DisabledToolButton
                        sx={{
                            paddingY: '0.375rem',
                            justifyContent: 'space-between',
                        }}
                        confirmdelete={`${confirmDelete}`}
                        variant="outlined"
                        fullWidth
                        disableRipple={true}
                        onClick={() => {
                            toggleTool(tool.id, tool.enabled);
                        }}
                    >
                        {tool.name}
                        {confirmDelete ? (
                            <Box>
                                <IconButton
                                    edge="end"
                                    color="white"
                                    sx={{
                                        fontSize: '0.8rem',
                                    }}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteTool(tool.id);
                                    }}
                                >
                                    <DoneIcon fontSize="inherit" />
                                </IconButton>
                                <IconButton
                                    edge="end"
                                    color="white"
                                    sx={{
                                        fontSize: '0.8rem',
                                        marginLeft: '0.6rem',
                                    }}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setConfirmDelete(false);
                                    }}
                                >
                                    <CancelIcon fontSize="inherit" />
                                </IconButton>
                            </Box>
                        ) : (
                            !tool.core && (
                                <IconButton
                                    edge="end"
                                    color="white"
                                    sx={{
                                        fontSize: '0.8rem',
                                    }}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setConfirmDelete(true);
                                    }}
                                >
                                    <DeleteIcon fontSize="inherit" />
                                </IconButton>
                            )
                        )}
                    </DisabledToolButton>
                </Box>
            )}
        </Box>
    );
}
