/* eslint-disable react-hooks/exhaustive-deps */
// frontend/src/App.tsx

import { useState, useEffect } from 'react';
import './App.css'; // 必要に応じてCSSファイルも確認するのじゃ

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

  // FastAPIのベースURLを環境変数から取得するのじゃ
  // .envファイルが読み込まれない場合、デフォルト値 'http://localhost:8000' が使われる
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // FastAPIのルートパスからのメッセージ取得 (コンポーネント初回マウント時)
  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (!response.ok) {
          throw new Error(`FastAPIルート取得エラー: ${response.status}`);
        }
        const data = await response.json();
        setMessage(data.message);
      } catch (err: unknown) {
        console.error("FastAPIメッセージ取得エラー:", err);
        if (err instanceof Error) {
          setMessage(`エラー: ${err.message}`);
        } else {
          setMessage('エラー: 不明なエラーが発生しました');
        }
      }
    };
    fetchMessage();
  }, [API_BASE_URL]); // API_BASE_URLが変更されたら再実行する

  // 天気データをFastAPI経由で取得する関数じゃ
  const fetchWeather = async () => {
    setLoading(true); // ロード中状態にする
    setError(null);   // エラーをリセット
    setWeather(null); // 前の天気データをクリア

    try {
      const response = await fetch(`${API_BASE_URL}/weather/${city}`);
      if (!response.ok) { // HTTPステータスコードが200番台以外の場合
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTPエラー: ${response.status}`);
      }
      const data: WeatherData = await response.json();
      setWeather(data); // 取得したデータをstateにセット
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message); // エラーメッセージをstateにセット
      } else {
        setError('不明なエラーが発生しました');
      }
      console.error("天気データ取得エラー:", err);
    } finally {
      setLoading(false); // ロード状態を解除
    }
  };

  // コンポーネントがマウントされたときに一度天気を取得するのじゃ
  // 初期表示と都市名が変更された場合に天気を再取得するように変更
  useEffect(() => {
    fetchWeather();
  }, [city]); // cityが変更されたら天気を再取得する (今回は初回起動時にも動作する)


  // 都市名入力フィールドの変更ハンドラ
  const handleCityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCity(e.target.value);
  };

  // フォーム送信ハンドラ
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // ページの再読み込みを防ぐ
    fetchWeather(); // 天気取得関数を呼び出す
  };

  return (
    <div className="App">
      <h1>FastAPI と React の連携じゃ！</h1>
      <p>FastAPIからのメッセージ: {message}</p>

      <h2>現在の天気情報</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={city}
          onChange={handleCityChange}
          placeholder="都市名を入力するのじゃ (例: Tokyo)"
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
          {weather.icon_url && <img src={weather.icon_url} alt={weather.description} style={{width: '100px', height: '100px'}} />}
        </div>
      )}

      {!weather && !loading && !error && (
        <p>都市の天気を入力して、取得ボタンを押すのじゃ！</p>
      )}
    </div>
  );
}

export default App;