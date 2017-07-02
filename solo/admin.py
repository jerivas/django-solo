from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def admin_url(model, url, object_id=None):
    """
    Returns the URL for the given model and admin url name.
    From mezzanine.utils.urls.admin_url.
    """
    opts = model._meta
    url = "admin:%s_%s_%s" % (opts.app_label, opts.object_name.lower(), url)
    args = ()
    if object_id is not None:
        args = (object_id,)
    return reverse(url, args=args)


class SingletonModelAdmin(admin.ModelAdmin):
    """
    Admin class for models that should only contain a single instance
    in the database. Redirect all views to the change view when the
    instance exists, and to the add view when it doesn't.
    From mezzanine.utils.admin.SingletonModelAdmin.
    """

    def handle_save(self, request, response):
        """
        Handles redirect back to the dashboard when save is clicked
        (eg not save and continue editing), by checking for a redirect
        response, which only occurs if the form is valid.
        """
        form_valid = isinstance(response, HttpResponseRedirect)
        if request.POST.get("_save") and form_valid:
            return redirect("admin:index")
        return response

    def changelist_view(self, *args, **kwargs):
        """
        Redirect to the add view if no records exist or the change
        view if the singleton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except self.model.MultipleObjectsReturned:
            return super(SingletonModelAdmin, self).changelist_view(*args, **kwargs)
        except self.model.DoesNotExist:
            return redirect(admin_url(self.model, "add"))
        return redirect(admin_url(self.model, "change", singleton.id))

    def has_add_permission(self, request):
        """
        Don't allow creating from the admin.
        Singleton models are created by the get_solo() class method.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable deleting.
        """
        return False
