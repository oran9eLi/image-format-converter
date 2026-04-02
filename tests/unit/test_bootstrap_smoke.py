from image_format_converter.app import build_app


def test_build_app_returns_qapplication(qapp):
    app = build_app([])
    assert app is qapp
