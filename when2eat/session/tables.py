import django_tables2 as tables
from django.contrib.auth.models import User

class UserTable(tables.Table):
    selection = tables.TemplateColumn('<input type="checkbox" name="selection" value={{ record.pk }} />', verbose_name="Must Attend", orderable=False)
    class Meta:
        model = User
        template_name = "django_tables2/bootstrap4.html"
        fields = ('first_name', 'last_name', 'email')
