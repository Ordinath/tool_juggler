import { Box, Button } from '@mui/material';
import Tool from './Tool';
import ZipFileDropzone from './ZipFileDropzone';

import { useConversations } from './ConversationsContext';

export default function ToolList() {
    // Add your tools here
    const { tools } = useConversations();

    return (
        <>
            {tools.length > 0 && tools.map((tool) => <Tool key={tool.id} tool={tool} />)}
            <Box width="100%" sx={{ paddingLeft: '2rem' }}>
                <ZipFileDropzone />
            </Box>
        </>
    );
}
