from django.urls import reverse, resolve

class TestUrls:

    def test_logout_url(self):
        """
        Prueba la función cerrar sesión de un usuario en concreto con las redirecciones entre templates
        :return: si la redireccion se llevó a cabo satisfactoriamente retorna OK, caso contrario retorna un mensaje de error
        """
        path = reverse('gestion:logout')
        assert resolve(path).view_name == 'gestion:logout', "Se ha producido un error. La vista no es la correcta para la url gestion:logout"

    def test_perfil_url(self):
        """
        Prueba la función ver perfil de un usuario en concreto con las redirecciones entre templates
        :return: si la redireccion se llevó a cabo satisfactoriamente retorna OK, caso contrario retorna un mensaje de error
        """
        path = reverse('gestion:perfil')
        assert resolve(path).view_name == 'gestion:perfil', "Se ha producido un error. La vista no es la correcta para la url gestion:perfil_user"

    def test_getUser_url(self):
        """
        Prueba la función obtener un usuario en concreto con las redirecciones entre templates
        :return: si la redireccion se llevó a cabo satisfactoriamente retorna OK, caso contrario retorna un mensaje de error
        """
        path = reverse('gestion:get_user', kwargs = {'pk': 2})
        assert resolve(path).view_name == 'gestion:get_user', "Se ha producido un error. La vista no es la correcta para la url gestion:get_user"
