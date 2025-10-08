import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (event) => {
        event.preventDefault();
        setLoading(true);
        setMessage('');

        const { error } = await supabase.auth.signInWithPassword({
            email: email,
            password: password,
        });

        if (error) {
            setMessage('Error: ' + error.message);
        } else {
            // If login is successful, the onAuthStateChange listener in App.js
            // will detect the new session and redirect to the dashboard.
            navigate('/dashboard');
        }
        setLoading(false);
    };

    return (
        <div>
            <h2>Login to PixClad</h2>
            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    style={{margin: '5px', padding: '8px'}} 
                />
                <br />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={{margin: '5px', padding: '8px'}} 
                />
                <br />
                <button type="submit" disabled={loading} style={{margin: '10px', padding: '10px 20px'}}>
                    {loading ? 'Logging in...' : 'Login'}
                </button>
            </form>
            {message && <p>{message}</p>}
            <p>
                Don't have an account? <a href="/register">Register here</a>
            </p>
            <p>
                <a href="/forgot-password">Forgot your password?</a> {/* <-- Add this link */}
            </p>
        </div>
    );
}

export default Login;