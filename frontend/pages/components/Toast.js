import React, { useContext } from 'react';
import { Snackbar, Alert } from '@mui/material';
import { useConversations } from './ConversationsContext';

function Toast() {
    const { toasts, removeToast } = useConversations();
    return (
        <>
            {toasts.map((toast) => (
                <Snackbar
                    key={toast.id}
                    open={true}
                    autoHideDuration={6000}
                    onClose={() => removeToast(toast.id)}
                    anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
                >
                    <Alert onClose={() => removeToast(toast.id)} severity={toast.type} sx={{ width: '100%' }}>
                        {toast.message}
                    </Alert>
                </Snackbar>
            ))}
        </>
    );
}

export default Toast;
