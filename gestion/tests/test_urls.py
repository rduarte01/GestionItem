from django.urls import reverse, resolve

class TestUrls():
    def test_logout_url(self):
        path = reverse('logout')
        assert resolve(path).view_name == 'logout'

    def test_perfil_url(self):
        path = reverse('perfil')
        assert resolve(path).view_name == 'perfil'

    def test_getUser_url(self):
        path = reverse('getUser')
        assert resolve(path).view_name == 'getUser'