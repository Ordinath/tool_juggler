import Head from 'next/head';
import React from 'react';
import { styled, alpha } from '@mui/material/styles';
import { ConversationProvider } from './components/ConversationsContext';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import themeOptions from './themeOptions';

import ConversationList from './components/ConversationList';
import UserInput from './components/UserInput';
import SelectedConversation from './components/SelectedConversation';
import ToolList from './components/ToolList';
import Toast from './components/Toast';

import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Settings from './components/Settings';
import { useHasMounted } from './hooks/useHasMounted';

const darkTheme = createTheme(themeOptions);

const SidebarBox = styled(Box)(({ theme }) => ({
    display: 'flex',
    flexDirection: 'column',
    width: '20rem',
    minWidth: '20rem',
    gap: '.5rem',
    padding: '.5rem',
    height: '100%',
    overflowY: 'auto',
    backgroundColor: 'rgba(0, 0, 0, 0.1)',
}));

const LeftSidebarBox = styled(SidebarBox)(({ theme }) => ({
    borderRight: `1px solid ${alpha(theme.palette.primary.main, 0.15)}`,
}));
const RightSidebarBox = styled(SidebarBox)(({ theme }) => ({
    borderLeft: `1px solid ${alpha(theme.palette.primary.main, 0.15)}`,
}));

export default function Home() {
    const hasMounted = useHasMounted();
    if (!hasMounted) {
        return null;
    }
    return (
        <>
            <ConversationProvider>
                <Head>
                    <title>My Assistant</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1" />
                    <link rel="icon" href="/favicon.ico" />
                </Head>
                <main>
                    <ThemeProvider theme={darkTheme}>
                        <Toast />
                        <CssBaseline />
                        <Box display="flex" width="100%" height="100vh">
                            <LeftSidebarBox>
                                <ConversationList />
                                <Settings />
                            </LeftSidebarBox>
                            <Box
                                display="flex"
                                flexDirection="column"
                                className="content-container"
                                width="100%"
                                gap=".5rem"
                                padding=".5rem"
                                sx={{
                                    marginX: '2rem',
                                    marginY: '2rem',
                                }}
                            >
                                <SelectedConversation />
                                <UserInput />
                            </Box>
                            <RightSidebarBox>
                                <ToolList />
                            </RightSidebarBox>
                        </Box>
                    </ThemeProvider>
                </main>
            </ConversationProvider>
        </>
    );
}
