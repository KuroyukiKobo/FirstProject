// frontend/src/auth.ts

import { useCallback, useEffect, useState } from 'react';
import { apiAuthGet, apiLoginPost, apiPost } from './apiClient';

// ----------------------------------------------------
// Pydanticモデルに対応するTypeScriptの型定義じゃ
// ----------------------------------------------------
interface UserProfile {
    id: number;
    username: string;
    email: string;
}

interface UserLoginData {
    username: string;
    password: string;
}

interface UserRegisterData {
    username: string;
    email: string;
    password: string;
}

// ----------------------------------------------------
// 認証トークンを管理するカスタムフックじゃ
// ----------------------------------------------------
export const useAuth = () => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [token, setToken] = useState<string | null>(null); // 初期値はnullにしておく
    const [loading, setLoading] = useState(true); // 初期ロード中はtrueにする
    const [error, setError] = useState<string | null>(null);

    // ログイン状態を検証するための関数じゃ
    // トークンを引数で受け取るように変更するのじゃ
    const fetchCurrentUser = useCallback(async (currentToken: string) => {
        if (!currentToken) {
            setUser(null);
            setLoading(false);
            return;
        }
        setLoading(true);
        try {
            const userData: UserProfile = await apiAuthGet('/users/me/', currentToken);
            setUser(userData);
            setError(null);
        } catch (err: any) {
            // トークンが無効な場合、ユーザー情報とトークンをクリアする
            setError('セッションの有効期限が切れたか、無効なトークンじゃ。');
            setUser(null);
            setToken(null);
            localStorage.removeItem('access_token');
        } finally {
            setLoading(false);
        }
    }, []); // 依存配列は空でよい

    // アプリケーション起動時に一度だけトークンを検証する
    useEffect(() => {
        const storedToken = localStorage.getItem('access_token');
        if (storedToken) {
            setToken(storedToken);
            fetchCurrentUser(storedToken);
        } else {
            setLoading(false); // トークンがなければロード完了
        }
    }, [fetchCurrentUser]);

    // ユーザー登録関数じゃ
    const register = async (data: UserRegisterData) => {
        setLoading(true);
        setError(null);
        try {
            const newUser = await apiPost('/register', data);
            setError(null);
            return newUser;
        } catch (err: any) {
            setError(err.message);
            throw err; // エラーを呼び出し元に伝える
        } finally {
            setLoading(false);
        }
    };

    // ログイン関数じゃ
    const login = async (data: UserLoginData) => {
        setLoading(true);
        setError(null);
        try {
            const formData = new URLSearchParams();
            formData.append('username', data.username);
            formData.append('password', data.password);

            const tokenData = await apiLoginPost('/token', formData);
            const newAccessToken = tokenData.access_token;

            localStorage.setItem('access_token', newAccessToken);
            setToken(newAccessToken); // トークンをstateにセット

            // ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
            // ここが重要じゃ！
            // ログイン成功後、新しいトークンを使ってすぐにユーザー情報を取得するのじゃ！
            await fetchCurrentUser(newAccessToken);
            // ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★

            setError(null);
        } catch (err: any) {
            setError(err.message);
            setToken(null);
            localStorage.removeItem('access_token');
            throw err; // 呼び出し元にエラーを伝える
        } finally {
            setLoading(false);
        }
    };

    // ログアウト関数じゃ
    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('access_token');
        setError(null);
    };

    return { user, login, logout, register, loading, error, token };
};
