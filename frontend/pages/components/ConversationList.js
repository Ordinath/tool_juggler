import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import SideBarConversation from './SideBarConversation';
import ZipFileDropzone from './ZipFileDropzone';

import { useConversations } from './ConversationsContext';

export default function ConversationList() {
    const { conversations, handleAddNewConversation } = useConversations();

    return (
        <>
            <Box width="100%" sx={{ paddingRight: '2rem' }}>
                <Button variant="outlined" fullWidth onClick={handleAddNewConversation}>
                    New conversation
                </Button>
            </Box>
            {conversations.length > 0 && conversations.map((conversation) => <SideBarConversation key={conversation.id} {...{ conversation }} />)}
            {/* <Box width="100%" sx={{ paddingRight: '2rem' }}>
                <ZipFileDropzone />
            </Box> */}
        </>
    );
}

/* <TextField
    variant="standard"
    color="primary"
    InputProps={{
        readOnly: true,
        // readOnly: !editMode,
        disableUnderline: true,
        style: {
            // fontSize: '1.25rem',
            border: 'none',
            pointerEvents: 'none',
        },
    }}
    value={conversation.title}
/> */
// <Box display="flex" flexDirection="row" width="100%">
//     <TextField
//         variant="standard"
//         // disabled={!editMode}
//         disabled={true}
//         color="primary"
//         InputProps={{
//             // readOnly: !editMode,
//             disableUnderline: true,
//             style: {
//                 // fontSize: '1.25rem',
//                 border: 'none',
//             },
//         }}
//         sx={{ flexGrow: 1 }}
//         value={conversation.title}
//         // onChange={(e) => setCurrentTitle(e.target.value)}
//         // onBlur={handleTitleChanged}
//         onKeyPress={(e) => {
//             if (e.key === 'Enter') {
//                 // handleTitleChanged();
//                 console.log('Enter pressed');
//             }
//         }}
//     />
// </Box>
