def test_supabase_client_importable():
    from supabase import create_client

    assert create_client is not None
