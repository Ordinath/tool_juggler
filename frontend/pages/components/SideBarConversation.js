import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import IconButton from '@mui/material/IconButton';
import Grid from '@mui/material/Grid';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import DoneIcon from '@mui/icons-material/Done';
import CancelIcon from '@mui/icons-material/Cancel';
import TurnedInNotIcon from '@mui/icons-material/TurnedInNot';
import TurnedInIcon from '@mui/icons-material/TurnedIn';
import Tooltip from '@mui/material/Tooltip';
import { useEffect, useState } from 'react';
import { styled, alpha } from '@mui/material/styles';
import { useConversations } from './ConversationsContext';

const StyledConversation = styled(OutlinedInput)(({ editmode, selected, confirmdelete, theme }) => ({
    '& .MuiInputBase-input.Mui-disabled': {
        WebkitTextFillColor: selected ? '#fff' : undefined,
    },
    border: confirmdelete === 'true' ? `.0875rem solid ${theme.palette.error.main}` : `.0875rem solid ${theme.palette.primary.main}`,
    backgroundColor: confirmdelete === 'true' ? alpha(theme.palette.error.main, 0.3) : alpha(theme.palette.secondary.main, 0.3),
}));

export default function SideBarConversation({ conversation }) {
    const {
        selectedConversation,
        setSelectedConversation,
        handleChangeConversationTitle,
        handleDeleteConversation,
        handleUpsertConversationEmbeddings,
        handleDeleteConversationEmbeddings,
    } = useConversations();
    const [editMode, setEditMode] = useState(false);
    const [confirmDelete, setConfirmDelete] = useState(false);
    const [newConversationTitle, setNewConversationTitle] = useState(conversation.title);

    // upon unselecting a conversation, reset editMode and confirmDelete
    useEffect(() => {
        if (setSelectedConversation !== conversation.id) {
            setEditMode(false);
            setConfirmDelete(false);
            setNewConversationTitle(conversation.title);
        }
    }, [selectedConversation]);

    return (
        <Box display="flex" flexDirection="column" gap="0.5rem" width="100%" sx={{ position: 'relative', paddingRight: '2rem' }}>
            {selectedConversation !== conversation.id ? (
                <Button
                    sx={{ paddingY: '0.375rem' }}
                    variant="outlined"
                    fullWidth
                    onClick={() => {
                        setSelectedConversation(conversation.id);
                    }}
                >
                    {conversation.title}
                </Button>
            ) : (
                <Grid container spacing={1} alignItems="flex-end">
                    <Grid item xs={12}>
                        <StyledConversation
                            editmode={`${editMode}`}
                            selected={true}
                            confirmdelete={`${confirmDelete}`}
                            fullWidth
                            disabled={!editMode}
                            onChange={(e) => {
                                setNewConversationTitle(e.target.value);
                            }}
                            size="small"
                            value={newConversationTitle}
                            sx={{
                                '& fieldset': { border: 'none' },
                                paddingRight: '6rem',
                            }}
                            endAdornment={
                                <InputAdornment position="end">
                                    {!editMode && !confirmDelete && (
                                        <>
                                            <IconButton
                                                edge="end"
                                                color="inherit"
                                                onClick={() => {
                                                    setEditMode(true);
                                                }}
                                                sx={{
                                                    fontSize: '0.8rem',
                                                    position: 'absolute',
                                                    bottom: 5.5,
                                                    right: 45,
                                                }}
                                            >
                                                <EditIcon fontSize="inherit" />
                                            </IconButton>
                                            <IconButton
                                                edge="end"
                                                color="inherit"
                                                onClick={() => {
                                                    setConfirmDelete(true);
                                                }}
                                                sx={{
                                                    fontSize: '0.8rem',
                                                    position: 'absolute',
                                                    bottom: 5.5,
                                                    right: 18,
                                                }}
                                            >
                                                <DeleteIcon fontSize="inherit" />
                                            </IconButton>
                                        </>
                                    )}
                                    {editMode && !confirmDelete && (
                                        <>
                                            <IconButton
                                                edge="end"
                                                color="inherit"
                                                onClick={() => {
                                                    handleChangeConversationTitle(conversation.id, newConversationTitle);
                                                    setEditMode(false);
                                                }}
                                                sx={{
                                                    fontSize: '0.8rem',
                                                    position: 'absolute',
                                                    bottom: 5.5,
                                                    right: 45,
                                                }}
                                            >
                                                <DoneIcon fontSize="inherit" />
                                            </IconButton>
                                            <IconButton
                                                edge="end"
                                                color="inherit"
                                                onClick={() => {
                                                    setNewConversationTitle(conversation.title);
                                                    setEditMode(false);
                                                }}
                                                sx={{
                                                    fontSize: '0.8rem',
                                                    position: 'absolute',
                                                    bottom: 5.5,
                                                    right: 18,
                                                }}
                                            >
                                                <CancelIcon fontSize="inherit" />
                                            </IconButton>
                                        </>
                                    )}
                                    {confirmDelete && (
                                        <>
                                            <IconButton
                                                edge="end"
                                                color="inherit"
                                                aria-label="send message"
                                                onClick={() => {
                                                    handleDeleteConversation(conversation.id);
                                                }}
                                                sx={{
                                                    fontSize: '0.8rem',
                                                    position: 'absolute',
                                                    bottom: 5.5,
                                                    right: 45,
                                                }}
                                            >
                                                <DoneIcon fontSize="inherit" />
                                            </IconButton>
                                            <IconButton
                                                edge="end"
                                                color="inherit"
                                                aria-label="send message"
                                                onClick={() => {
                                                    setConfirmDelete(false);
                                                }}
                                                sx={{
                                                    fontSize: '0.8rem',
                                                    position: 'absolute',
                                                    bottom: 5.5,
                                                    right: 18,
                                                }}
                                            >
                                                <CancelIcon fontSize="inherit" />
                                            </IconButton>
                                        </>
                                    )}
                                </InputAdornment>
                            }
                        />
                    </Grid>
                </Grid>
            )}
            <Tooltip title="Toggle to remember conversation in long term memory" enterDelay={250}>
                <IconButton
                    edge="end"
                    color="inherit"
                    onClick={() => {
                        if (conversation.embedded) {
                            handleDeleteConversationEmbeddings(conversation.id);
                        } else {
                            handleUpsertConversationEmbeddings(conversation.id);
                        }
                    }}
                    sx={{
                        fontSize: '0.9rem',
                        position: 'absolute',
                        bottom: 5.5,
                        left: 270,
                    }}
                >
                    {conversation.embedded ? <TurnedInIcon fontSize="inherit" color="primary" /> : <TurnedInNotIcon fontSize="inherit" color="warning" />}
                </IconButton>
            </Tooltip>
        </Box>
    );
}
