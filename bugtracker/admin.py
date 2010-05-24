from django.contrib import admin
from urtest.bugtracker.models import Bug, Project, ProjectFile, BugFile

class BugAdmin(admin.ModelAdmin):
    pass

class ProjectAdmin(admin.ModelAdmin):
    pass

class ProjectFileAdmin(admin.ModelAdmin):
    pass

class BugFileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Bug, BugAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectFile, ProjectFileAdmin)
admin.site.register(BugFile, BugFileAdmin)
