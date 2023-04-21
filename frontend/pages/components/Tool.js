import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { styled, alpha } from '@mui/material/styles';
import { useConversations } from './ConversationsContext';
// import { ToggleOn, ToggleOff } from '@mui/icons-material';

const EnabledToolButton = styled(Button)(({ theme }) => ({
    backgroundColor: alpha(theme.palette.secondary.main, 0.3),
    color: '#fff',
    border: `.0875rem solid ${theme.palette.primary.main}`,
}));

const DisabledToolButton = styled(Button)(({ theme }) => ({}));

export default function Tool({ tool }) {
    const { toggleTool } = useConversations();
    return (
        <Box key={tool.id} width="100%" sx={{ position: 'relative', paddingLeft: '2rem' }}>
            {tool.enabled ? (
                <Box width="100%">
                    <EnabledToolButton
                        sx={{
                            paddingY: '0.375rem',
                            justifyContent: 'flex-end',
                            // backgroundColor: alpha(theme.palette.secondary.main, 0.3),
                        }}
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
                            justifyContent: 'flex-end',
                        }}
                        variant="outlined"
                        fullWidth
                        onClick={() => {
                            toggleTool(tool.id, tool.enabled);
                        }}
                    >
                        {tool.name}
                    </DisabledToolButton>
                </Box>
            )}
        </Box>
    );
}
