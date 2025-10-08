import { useState } from 'react';
import { supabase } from '../supabaseClient';

function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handlePasswordReset = async (event) => {
        event.preventDefault();
        setLoading(true);
        setMessage('');

        const { error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: 'http://localhost:3000/update-password',
        });

        if (error) {
            setMessage('Error: ' + error.message);
        } else {
            setMessage('Password reset link has been sent to your email.');
        }
        setLoading(false);
    };

    return (
        <div>
            <h2>Forgot Password</h2>
            <p>Enter your email to receive a password reset link.</p>
            <form onSubmit={handlePasswordReset}>
                <input
                    type="email"
                    placeholder="Your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    style={{margin: '5px', padding: '8px'}}
                />
                <br />
                <button type="submit" disabled={loading} style={{margin: '10px', padding: '10px 20px'}}>
                    {loading ? 'Sending...' : 'Send Reset Link'}
                </button>
            </form>
            {message && <p>{message}</p>}
            <a href="/login">Back to Login</a>
        </div>
    );
}

export default ForgotPassword;