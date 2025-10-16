from django.contrib import admin


class MyAdminSite(admin.AdminSite):
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)

        # Define your custom ordering
        app_order = [
            'research_problems',
            'search',
            'services',
            'equipment',
            'documents',
            'infrastructures',
            'institutions',
            'locations',
            'access',
            'specifications',
            'audit',
            'taxonomy',
            'users',
            'api',
            'matching',
            'scheduling',
        ]

        # Sort the app list
        app_list = sorted(app_dict.values(), key=lambda x:
            app_order.index(x['app_label']) if x['app_label'] in app_order else 999
                          )

        return app_list


# Create an instance of your custom admin site
admin_site = MyAdminSite(name='myadmin')