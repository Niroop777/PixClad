import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient'; // Import our supabase client

function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (event) => {
        event.preventDefault();
        setLoading(true);
        setMessage('');

        const { error } = await supabase.auth.signUp({
            email: email,
            password: password,
        });

        if (error) {
            setMessage('Error: ' + error.message);
        } else {
            setMessage('Registration successful! Please check your email for a verification link.');
            // Optionally, you can redirect the user after a delay
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        }
        setLoading(false);
    };

    return (
        <div>
            <h2>Register for PixClad</h2>
            <form onSubmit={handleRegister}>
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
                    placeholder="Password (at least 6 characters)" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={{margin: '5px', padding: '8px'}} 
                />
                <br />
                <button type="submit" disabled={loading} style={{margin: '10px', padding: '10px 20px'}}>
                    {loading ? 'Registering...' : 'Register'}
                </button>
            </form>
            {message && <p>{message}</p>}
            <p>
                Already have an account? <a href="/login">Login here</a>
            </p>
        </div>
    );
}

export default Register;