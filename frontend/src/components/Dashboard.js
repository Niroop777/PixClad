// import { useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import axios from 'axios';
// import { supabase } from '../supabaseClient';
// import Uploader from './Uploader';

// function Dashboard({ session }) {
//     const navigate = useNavigate();
//     const [gdriveFolders, setGdriveFolders] = useState([]);
//     const [isLoadingFolders, setIsLoadingFolders] = useState(false);
//     const [isProcessing, setIsProcessing] = useState(false);
//     const [processMessage, setProcessMessage] = useState('');
//     const [processResults, setProcessResults] = useState({});
//     const [gdriveDestination, setGdriveDestination] = useState('local'); // New state for G-Drive destination

//     const handleLogout = async () => {
//         await supabase.auth.signOut();
//         navigate('/login');
//     };

//     const fetchGdriveFolders = async () => {
//         setIsLoadingFolders(true);
//         setProcessMessage('');
//         setProcessResults({});
//         try {
//             const response = await axios.get('http://localhost:5001/auth/gdrive/files', { withCredentials: true });
//             setGdriveFolders(response.data);
//         } catch (error) {
//             console.error("Could not fetch Google Drive folders:", error);
//             alert("Failed to fetch folders. Please try reconnecting.");
//         }
//         setIsLoadingFolders(false);
//     };

//     const handleProcessFolder = async (folderId, folderName) => {
//         setIsProcessing(true);
//         setProcessMessage(`Processing folder: "${folderName}"...`);
//         setProcessResults({});
//         try {
//             // Send the destination choice in the request body
//             const response = await axios.post(
//                 `http://localhost:5001/auth/gdrive/process-folder/${folderId}`,
//                 { destination: gdriveDestination }, // <-- Send destination here
//                 { withCredentials: true }
//             );
//             setProcessMessage(response.data.message);
//             setProcessResults(response.data.results || {});
//         } catch (error) {
//             console.error("Failed to process folder:", error);
//             setProcessMessage("Error processing folder.");
//         }
//         setIsProcessing(false);
//     };

//     return (
//         <div style={{ padding: '0 20px' }}>
//             <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>
//                 <h4>Welcome, {session?.user?.email}!</h4>
//                 <button onClick={handleLogout} style={{ backgroundColor: '#f44336', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '5px', cursor: 'pointer' }}>
//                     Logout
//                 </button>
//             </header>
            
//             <div style={{margin: '20px 0', padding: '20px', border: '1px solid #eee', borderRadius: '8px', textAlign: 'center'}}>
//                 <h3>Process a Google Drive Folder</h3>
//                 <a href="http://localhost:5001/auth/gdrive/login">
//                     <button style={{marginRight: '10px'}}>Connect/Reconnect Google Drive</button>
//                 </a>
//                 <button onClick={fetchGdriveFolders} disabled={isLoadingFolders}>
//                     {isLoadingFolders ? 'Loading...' : 'Fetch Folders'}
//                 </button>
                
//                 {gdriveFolders.length > 0 && (
//                     <div style={{marginTop: '10px'}}>
//                         {/* --- Add G-Drive Destination Selector --- */}
//                         <div style={{margin: '10px 0'}}>
//                             <label>Destination: </label>
//                             <select value={gdriveDestination} onChange={(e) => setGdriveDestination(e.target.value)}>
//                                 <option value="local">Local Folder</option>
//                                 <option value="gdrive">Google Drive</option>
//                             </select>
//                         </div>
//                         <h4>Click a folder to process:</h4>
//                         <ul style={{listStyleType: 'none', padding: 0, textAlign: 'left', maxHeight: '150px', overflowY: 'auto', border: '1px solid #ddd'}}>
//                             {gdriveFolders.map(folder => (
//                                 <li key={folder.id} 
//                                     onClick={() => !isProcessing && handleProcessFolder(folder.id, folder.name)}
//                                     style={{padding: '10px', borderBottom: '1px solid #ddd', cursor: isProcessing ? 'not-allowed' : 'pointer', backgroundColor: isProcessing ? '#f9f9f9' : '#fff'}}
//                                 >
//                                     📁 {folder.name}
//                                 </li>
//                             ))}
//                         </ul>
//                     </div>
//                 )}

//                 {processMessage && <p><strong>{processMessage}</strong></p>}
                
//                 {Object.keys(processResults).length > 0 && (
//                     <div style={{marginTop: '10px', textAlign: 'left'}}>
//                         <h5>Processing Details:</h5>
//                         <ul style={{ listStyleType: 'none', padding: 0, maxHeight: '150px', overflowY: 'auto', border: '1px solid #eee' }}>
//                             {Object.entries(processResults).map(([filename, tags]) => (
//                                 <li key={filename} style={{ background: '#f9f9f9', margin: '5px', padding: '8px', borderRadius: '5px' }}>
//                                     <strong>{filename}:</strong> Moved to folder '{tags[0] || 'Uncategorized'}'
//                                 </li>
//                             ))}
//                         </ul>
//                     </div>
//                 )}
//             </div>

//             <div style={{marginTop: '40px'}}>
//                 <Uploader />
//             </div>
//         </div>
//     );
// }

// export default Dashboard;


import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { supabase } from '../supabaseClient';
import Uploader from './Uploader';

function Dashboard({ session }) {
    const navigate = useNavigate();
    const [gdriveFolders, setGdriveFolders] = useState([]);
    const [isLoadingFolders, setIsLoadingFolders] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [processMessage, setProcessMessage] = useState('');
    const [processResults, setProcessResults] = useState({});
    const [gdriveDestination, setGdriveDestination] = useState('local');

    const handleLogout = async () => {
        await supabase.auth.signOut();
        navigate('/login');
    };

    const fetchGdriveFolders = async () => {
        setIsLoadingFolders(true);
        setProcessMessage('');
        setProcessResults({});
        try {
            const response = await axios.get('http://localhost:5001/auth/gdrive/files', { withCredentials: true });
            setGdriveFolders(response.data);
        } catch (error) {
            console.error("Could not fetch Google Drive folders:", error);
            alert("Failed to fetch folders. Please try reconnecting.");
        }
        setIsLoadingFolders(false);
    };

    const handleProcessFolder = async (folderId, folderName) => {
        setIsProcessing(true);
        setProcessMessage(`Processing folder: "${folderName}"...`);
        setProcessResults({});
        try {
            // The data is the second argument, the config is the third.
            const response = await axios.post(
                `http://localhost:5001/auth/gdrive/process-folder/${folderId}`,
                { destination: gdriveDestination }, // Request body
                { withCredentials: true }           // Request config
            );
            setProcessMessage(response.data.message);
            setProcessResults(response.data.results || {});
        } catch (error) {
            console.error("Failed to process folder:", error);
            setProcessMessage("Error processing folder.");
        }
        setIsProcessing(false);
    };

    return (
        <div style={{ padding: '0 20px' }}>
            {/* Header */}
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>
                <h4>Welcome, {session?.user?.email}!</h4>
                <button onClick={handleLogout} style={{ backgroundColor: '#f44336', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '5px', cursor: 'pointer' }}>Logout</button>
            </header>
            
            {/* Google Drive Section */}
            <div style={{margin: '20px 0', padding: '20px', border: '1px solid #eee', borderRadius: '8px', textAlign: 'center'}}>
                <h3>Process a Google Drive Folder</h3>
                <a href="http://localhost:5001/auth/gdrive/login"><button style={{marginRight: '10px'}}>Connect/Reconnect</button></a>
                <button onClick={fetchGdriveFolders} disabled={isLoadingFolders}>{isLoadingFolders ? 'Loading...' : 'Fetch Folders'}</button>
                
                {gdriveFolders.length > 0 && (
                    <div style={{marginTop: '10px'}}>
                        <div style={{margin: '10px 0'}}>
                            <label>Destination: </label>
                            <select value={gdriveDestination} onChange={(e) => setGdriveDestination(e.target.value)}>
                                <option value="local">Local Folder</option>
                                <option value="gdrive">Google Drive</option>
                            </select>
                        </div>
                        <h4>Click a folder to process:</h4>
                        <ul style={{listStyleType: 'none', padding: 0, textAlign: 'left', maxHeight: '150px', overflowY: 'auto', border: '1px solid #ddd'}}>
                            {gdriveFolders.map(folder => (
                                <li key={folder.id} onClick={() => !isProcessing && handleProcessFolder(folder.id, folder.name)} style={{padding: '10px', borderBottom: '1px solid #ddd', cursor: isProcessing ? 'not-allowed' : 'pointer' }}>
                                    📁 {folder.name}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {processMessage && <p><strong>{processMessage}</strong></p>}
                
                {Object.keys(processResults).length > 0 && (
                    <div style={{marginTop: '10px', textAlign: 'left'}}>
                        <h5>Processing Details:</h5>
                        <ul style={{ listStyleType: 'none', padding: 0, maxHeight: '150px', overflowY: 'auto', border: '1px solid #eee' }}>
                            {Object.entries(processResults).map(([filename, tags]) => (
                                <li key={filename} style={{ background: '#f9f9f9', margin: '5px', padding: '8px', borderRadius: '5px' }}>
                                    <strong>{filename}:</strong> Moved to folder '{tags[0] || 'Uncategorized'}'
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Local Uploader Section */}
            <div style={{marginTop: '40px'}}><Uploader /></div>
        </div>
    );
}

export default Dashboard;