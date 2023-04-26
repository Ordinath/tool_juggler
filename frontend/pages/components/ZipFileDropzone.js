import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useConversations } from './ConversationsContext';
import CircularProgress from '@mui/material/CircularProgress';

const ZipFileDropzone = ({ onDrop }) => {
    const { handleToolZipDrop } = useConversations();
    const [isLoading, setIsLoading] = useState(false);
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop: async (acceptedFiles) => {
            setIsLoading(true);
            try {
                await handleToolZipDrop(acceptedFiles);
            } catch (error) {
                console.error('Error uploading the file:', error);
            }
            setIsLoading(false);
        },
        accept: 'application/zip',
    });

    return (
        <div
            {...getRootProps()}
            style={{
                border: '2px dashed gray',
                padding: '10px',
                textAlign: 'center',
                borderRadius: '4px',
                height: '100px',
                pointerEvents: isLoading ? 'none' : 'auto',
                opacity: isLoading ? 0.5 : 1,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
            }}
        >
            <input {...getInputProps()} />
            {isLoading ? (
                <CircularProgress />
            ) : isDragActive ? (
                <p>Drop the 📦 here...</p>
            ) : (
                <p>Upload a tool <b style={{color: 'red'}}>ZIP</b> file or a <b style={{color: 'red'}}>PDF</b> doc here.</p>
            )}
        </div>
    );
};

export default ZipFileDropzone;
