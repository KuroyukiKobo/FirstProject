// frontend/src/components/LoginForm.tsx

import React, { useState } from 'react';
import { useAuth } from '../auth';

interface LoginFormProps {
    onLoginSuccess: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLoginSuccess }) => {
    const { login, loading, error } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await login({ username, password });
            onLoginSuccess(); // ログイン成功時に親コンポーネントに通知する
        } catch (err) {
            // エラーはuseAuthフックで処理されるゆえ、ここでは特に何もしない
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '300px', margin: 'auto' }}>
            <h2>ログインじゃ！</h2>
            <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="ユーザー名"
                required
                disabled={loading}
            />
            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="パスワード"
                required
                disabled={loading}
            />
            <button type="submit" disabled={loading}>
                {loading ? 'ログイン中...' : 'ログイン'}
            </button>
            {error && <p style={{ color: 'red' }}>エラー: {JSON.stringify(error)}</p>}
        </form>
    );
};

export default LoginForm;