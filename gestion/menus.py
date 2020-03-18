from menu import Menu, MenuItem

"""
La Menu clase expone un método de clase llamado add_itemque acepta dos argumentos; 
el nombre del menú al que desea agregar y el MenuItemque va a agregar.
"""

from django.core.urlresolvers import resolve


class ViewMenuItem(MenuItem):
    """Custom MenuItem that checks permissions based on the view associated
    with a URL"""

    def check(self, request):
         """Check permissions based on our view"""
         is_visible = True
         match = resolve(self.url)

         # do something with match, and possibly change is_visible...

         self.visible = is_visible

