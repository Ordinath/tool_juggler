import React from 'react';
import { useDropzone } from 'react-dropzone';
import { useConversations } from './ConversationsContext';

const ZipFileDropzone = ({ onDrop }) => {
    const { handleToolZipDrop } = useConversations();
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop: handleToolZipDrop,
        accept: 'application/zip',
    });

    return (
        <div {...getRootProps()} style={{ border: '2px dashed gray', padding: '10px', textAlign: 'center', borderRadius: '4px', height: '100px' }}>
            <input {...getInputProps()} />
            {isDragActive ? <p>Drop the tool zip file here ...</p> : <p>Drag and drop a tool zip file here, or click to select a file</p>}
        </div>
    );
};

export default ZipFileDropzone;
