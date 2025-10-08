import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';

function UpdatePassword() {
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleUpdatePassword = async (event) => {
        event.preventDefault();
        setLoading(true);
        setMessage('');

        const { error } = await supabase.auth.updateUser({
            password: password
        });

        if (error) {
            setMessage('Error: ' + error.message);
        } else {
            setMessage('Password updated successfully! Redirecting to login...');
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        }
        setLoading(false);
    };

    return (
        <div>
            <h2>Update Your Password</h2>
            <p>Enter a new password below.</p>
            <form onSubmit={handleUpdatePassword}>
                <input
                    type="password"
                    placeholder="New password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={{margin: '5px', padding: '8px'}}
                />
                <br />
                <button type="submit" disabled={loading} style={{margin: '10px', padding: '10px 20px'}}>
                    {loading ? 'Updating...' : 'Update Password'}
                </button>
            </form>
            {message && <p>{message}</p>}
        </div>
    );
}

export default UpdatePassword;