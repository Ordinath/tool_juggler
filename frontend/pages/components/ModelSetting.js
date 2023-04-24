import Box from '@mui/material/Box';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Typography from '@mui/material/Typography';

import { useConversations } from './ConversationsContext';

export default function ModelSetting() {
    const { MODELS, selectedModel, setSelectedModel } = useConversations();

    const handleSelectedModelChange = (event) => {
        console.log('selected model', event.target.value);
        setSelectedModel(event.target.value);
    };
    return (
        <Box
            display="flex"
            flexDirection="column"
            gap="0.5rem"
            width="100%"
            sx={{
                borderTop: '1px solid #e0e0e0',
                paddingY: '0.5rem',
            }}
        >
            <Typography
                sx={{
                    textAlign: 'center',
                }}
            >
                Model
            </Typography>
            <FormControl fullWidth>
                <InputLabel
                    id="select-model-label"
                    sx={{
                        fontSize: '0.8rem',
                    }}
                >
                    Select Model
                </InputLabel>
                <Select
                    label="Select Model"
                    labelId="select-model-label"
                    sx={{
                        fontSize: '0.8rem',
                    }}
                    value={selectedModel}
                    onChange={handleSelectedModelChange}
                    size="small"
                >
                    {MODELS.map((model, index) => (
                        <MenuItem key={index} value={model.value}>
                            {model.name}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
        </Box>
    );
}
