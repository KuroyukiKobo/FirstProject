// frontend/src/components/RegisterForm.tsx

import React, { useState } from 'react';
import { useAuth } from '../auth';

const RegisterForm: React.FC = () => {
    const { register, loading, error } = useAuth();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSuccess(false);
        try {
            await register({ username, email, password });
            setSuccess(true);
            setUsername(''); // フォームをクリア
            setEmail('');
            setPassword('');
        } catch (err) {
            // エラーはuseAuthフックで処理される
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '300px', margin: 'auto' }}>
            <h2>ユーザー登録じゃ！</h2>
            <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="ユーザー名"
                required
                disabled={loading}
            />
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="メールアドレス"
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
                {loading ? '登録中...' : '登録'}
            </button>
            {success && <p style={{ color: 'green' }}>登録成功じゃ！ログインしてくれ。</p>}
            {error && <p style={{ color: 'red' }}>エラー: {error}</p>}
        </form>
    );
};

export default RegisterForm;