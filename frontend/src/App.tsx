// frontend/src/App.tsx

import { useState, useEffect } from 'react';
import './App.css';
import { useAuth } from './auth'; // <-- これをインポート！
import LoginForm from './components/LoginForm'; // <-- これをインポート！
import RegisterForm from './components/RegisterForm'; // <-- これをインポート！

// FastAPIから取得する天気データの型定義じゃ
interface WeatherData {
  city_name: string;
  temperature: number;
  description: string;
  icon_url: string;
}

function App() {
  const [message, setMessage] = useState('');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [city, setCity] = useState('Tokyo'); // デフォルト都市を東京にするのじゃ
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 認証フックを使用するのじゃ！
  const { user, logout, loading: authLoading, error: authError } = useAuth();

  // FastAPIのベースURLを環境変数から取得する
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost';

  // FastAPIのルートパスからのメッセージ取得 (コンポーネント初回マウント時)
  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/`);
        if (!response.ok) {
          // ↓↓↓ ここも修正するのじゃ！ ↓↓↓
          throw new Error(`FastAPIルート取得エラー: ${response.status}`);
        }
        const data = await response.json();
        setMessage(data.message);
      } catch (err: any) {
        console.error("FastAPIメッセージ取得エラー:", err);
        setMessage(`エラー: ${err.message}`);
      }
    };
    fetchMessage();
  }, [API_BASE_URL]);

  // 天気データをFastAPI経由で取得する関数じゃ
  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    setWeather(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/weather/${city}`);
      // 修正する行はこれじゃ！
      if (!response.ok) { // これでも良いが、より詳細なエラーハンドリング
        const errorData = await response.json();
        // ↓↓↓ ここを修正するのじゃ！ ↓↓↓
        throw new Error(errorData.detail || `HTTPエラー: ${response.status}`);
      }
      const data: WeatherData = await response.json();
      setWeather(data);
    } catch (err: any) {
      setError(err.message);
      console.error("天気データ取得エラー:", err);
    } finally {
      setLoading(false);
    }
  };

  // コンポーネントがマウントされたときに一度天気を取得する
  useEffect(() => {
    fetchWeather();
  }, [city]);


  // 都市名入力フィールドの変更ハンドラ
  const handleCityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCity(e.target.value);
  };

  // フォーム送信ハンドラ
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    fetchWeather();
  };

  const handleLoginSuccess = () => {
    console.log("ログイン成功じゃ！");
  };

  return (
    <div className="App">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px', borderBottom: '1px solid #ccc' }}>
        <h1>FastAPI と React の連携じゃ！</h1>
        {authLoading ? (
          <p>認証中...</p>
        ) : user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <p>ようこそ、{user.username}殿！</p>
            <button onClick={logout}>ログアウト</button>
          </div>
        ) : (
          <p>ログインしておらぬ...</p>
        )}
      </header>

      <main style={{ padding: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
        {/* ユーザー登録フォーム */}
        <section>
          <RegisterForm />
        </section>

        {/* ログインフォーム */}
        <section>
          <LoginForm onLoginSuccess={handleLoginSuccess} />
        </section>
      </main>

      <section style={{ marginTop: '40px', padding: '20px' }}>
        <p>FastAPIからのメッセージ: {message}</p>
        <h2>現在の天気情報</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={city}
            onChange={handleCityChange}
            placeholder="都市名を入力するのじゃ (例: Tokyo)"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? '取得中...' : '天気を取得！'}
          </button>
        </form>

        {error && <p style={{ color: 'red' }}>エラー: {error}</p>}
        {loading && <p>天気を取得中じゃ...</p>}

        {weather && (
          <div>
            <h3>{weather.city_name} の天気</h3>
            <p>気温: {weather.temperature}℃</p>
            <p>説明: {weather.description}</p>
            {weather.icon_url && <img src={weather.icon_url} alt={weather.description} style={{ width: '100px', height: '100px' }} />}
          </div>
        )}

        {!weather && !loading && !error && (
          <p>都市の天気を入力して、取得ボタンを押すのじゃ！</p>
        )}
      </section>

      {authError && <div style={{ position: 'fixed', bottom: '20px', left: '20px', background: 'rgba(255, 0, 0, 0.8)', color: 'white', padding: '15px', borderRadius: '5px' }}>
        認証エラー: {authError}
      </div>}
    </div>
  );
}

export default App;