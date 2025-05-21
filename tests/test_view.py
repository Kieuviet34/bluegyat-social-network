def test_home_page(client):
    """
    Kiểm tra GET / trả về 200 và render template index.html
    """
    resp = client.get('/')
    assert resp.status_code == 200
    # Với template mẫu, có thể kiểm tra tiêu đề hoặc đoạn welcome text
    assert b'Welcome to BlueGyat' in resp.data or b'No posts yet' in resp.data
