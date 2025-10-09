

import { useState, useRef } from 'react';
import axios from 'axios';

function Uploader() {
    const [files, setFiles] = useState([]);
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState({});
    const [destination, setDestination] = useState('local'); // New state for destination

    const fileInputRef = useRef(null);
    const folderInputRef = useRef(null);

    const handleFileChange = (event) => {
        setFiles(Array.from(event.target.files));
        setMessage('');
        setResults({});
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            setMessage('Please select files or a folder first!');
            return;
        }

        setIsLoading(true);
        const fileCount = files.length;
        const uploadType = fileCount === 1 ? 'file' : 'files';
        setMessage(`Processing ${fileCount} ${uploadType}... this may take a while.`);

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });
        formData.append('destination', destination); // <-- Add destination to the form data

        try {
            const response = await axios.post('https://pixclad.onrender.com/process-upload', formData, {
                withCredentials: true // <-- Make sure this is here
            });
            setResults(response.data.results);
            setMessage('Processing complete!');
        } catch (error) {
            console.error('Error uploading:', error);
            // More specific error for GDrive auth failure
            if (error.response && error.response.status === 401) {
                setMessage('Error: Google Drive not connected. Please connect your account.');
            } else {
                setMessage('Error: Could not process the upload.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '700px', margin: 'auto', border: '1px solid #ddd', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h3>Upload Files or a Folder for AI Sorting</h3>
            
            {/* --- Add Destination Selector --- */}
            <div style={{margin: '15px 0'}}>
                <label><strong>Destination: </strong></label>
                <select value={destination} onChange={(e) => setDestination(e.target.value)} style={{padding: '5px', marginLeft: '5px'}}>
                    <option value="local">Local Folder</option>
                    <option value="gdrive">Google Drive</option>
                </select>
            </div>

            <div style={{ margin: '20px 0' }}>
                <button onClick={() => fileInputRef.current.click()} style={{ marginRight: '10px' }}>
                    Select File(s)
                </button>
                <button onClick={() => folderInputRef.current.click()}>
                    Select Folder
                </button>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} multiple style={{ display: 'none' }} />
                <input type="file" ref={folderInputRef} onChange={handleFileChange} webkitdirectory="true" directory="true" style={{ display: 'none' }} />
            </div>
            
            {files.length > 0 && <p>{files.length} item(s) selected.</p>}
            <button onClick={handleUpload} disabled={isLoading || files.length === 0}>
                {isLoading ? 'Processing...' : `Process Upload`}
            </button>
            
            {message && <p>{message}</p>}
            
            {Object.keys(results).length > 0 && (
                <div style={{marginTop: '20px', textAlign: 'left'}}>
                    <h4>Processing Results:</h4>
                    <ul style={{ listStyleType: 'none', padding: 0, maxHeight: '200px', overflowY: 'auto', border: '1px solid #eee' }}>
                        {Object.entries(results).map(([filename, tags]) => (
                            <li key={filename} style={{ background: '#f0f0f0', margin: '5px', padding: '10px', borderRadius: '5px' }}>
                                <strong>{filename}:</strong> Moved to folder '{tags[0] || 'Uncategorized'}'
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default Uploader;