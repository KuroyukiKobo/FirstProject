// FastAPIのベースURLを環境変数から取得する
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost";

// APIクライアントの基本関数じゃ
// この関数は、FastAPIへのリクエストに共通の処理を追加する
async function apiFetch(endpoint: string, options?: RequestInit) {
    // オプションがあれば、デフォルトのヘッダーなどを追加する
    const headers = new Headers(options?.headers);
    if (!headers.has('Content-Type')) {
        headers.append('Content-Type', 'application/json');
    }
    // リクエストURLを構築する。Nginxのリバースプロキシを考慮して '/api' を追加する
    const url = `${API_BASE_URL}/api${endpoint}`;

    // fetchを呼び出すのじゃ
    const response = await fetch(url, {
        ...options,
        headers,
    });

    // レスポンスが成功（200番台）でなければ、エラーをスローする
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTPエラー: ${response.status}`);
    }

    // レスポンスのJSONデータを返す
    return response.json();
}

// GETリクエスト用の関数
export const apiGet = (endpoint: string) => {
    return apiFetch(endpoint, { method: "GET" });
};

// POSTリクエスト用の関数
export const apiPost = (endpoint: string, data: any) => {
    return apiFetch(endpoint, {
        method: "POST",
        body: JSON.stringify(data),
    });
};

// PUTリクエスト用の関数
export const apiPut = (endpoint: string, data: any) => {
    return apiFetch(endpoint, {
        method: "PUT",
        body: JSON.stringify(data),
    });
};

// OAuth2ログイン用のPOST関数を追加するのじゃ
// ヘッダーを特別に設定できる
export const apiLoginPost = (endpoint: string, data: URLSearchParams) => {
    return apiFetch(endpoint, {
        method: 'POST',
        body: data,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });
};

// 認証トークンをヘッダーに含めてGETリクエストを送る関数
export const apiAuthGet = (endpoint: string, token: string) => {
    return apiFetch(endpoint, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
};
