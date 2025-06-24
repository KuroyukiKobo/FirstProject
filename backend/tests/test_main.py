# C:\src\FirstProject\backend\tests\test_main.py

# テスト関数に client_with_db フィクスチャを渡すのじゃ
def test_read_main(client_with_db):
    response = client_with_db.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ハロー、先生！FastAPIバックエンドが起動しておるぞ！"}

def test_create_user(client_with_db):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client_with_db.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert "id" in response.json() # IDが返ってくるか確認

    # 作成したユーザーが取得できるかテスト
    response = client_with_db.get(f"/users/{user_data['username']}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    # assert response.json()["email"] == user_data["email"] # emailも確認