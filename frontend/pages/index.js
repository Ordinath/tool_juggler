import Head from 'next/head';
import React, { useEffect, useState } from 'react';
import { ConversationProvider } from './components/ConversationsContext';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import themeOptions from './themeOptions';

import ConversationList from './components/ConversationList';
import UserInput from './components/UserInput';
import SelectedConversation from './components/SelectedConversation';
import ToolList from './components/ToolList';

import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Settings from './components/Settings';

const darkTheme = createTheme(themeOptions);

export default function Home() {
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
                        <CssBaseline />
                        <Box display="flex" width="100%" height="100vh">
                            <Box
                                display="flex"
                                flexDirection="column"
                                // flexWrap="wrap"
                                className="sidebar"
                                width="20rem"
                                minWidth="20rem"
                                gap=".5rem"
                                padding=".5rem"
                                // height="100%"
                                sx={{ backgroundColor: 'rgba(0, 0, 0, 0.1)' }}
                                // sx={{ overflowY: 'scroll', backgroundColor: 'rgba(0, 0, 0, 0.1)' }}
                            >
                                <ConversationList {...{}} />
                                <Settings />
                            </Box>
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
                                <SelectedConversation {...{}} />
                                <UserInput {...{}} />
                            </Box>
                            <Box
                                display="flex"
                                flexDirection="column"
                                flexWrap="wrap"
                                className="sidebar"
                                width="20rem"
                                minWidth="20rem"
                                gap=".5rem"
                                padding=".5rem"
                                height="100%"
                                sx={{ overflowY: 'auto', backgroundColor: 'rgba(0, 0, 0, 0.1)' }}
                            >
                                <ToolList />
                            </Box>
                        </Box>
                    </ThemeProvider>
                </main>
            </ConversationProvider>
        </>
    );
}
