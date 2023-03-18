import shutil

from django.contrib import admin

from django.db.models.query import QuerySet

from coreapp.middleware import Request

from .models.github import GitHubUser

from .models.profile import Profile
from .models.scratch import Asm, Assembly, CompilerConfig, Scratch
from .models.course import Course, CourseChapter, CourseScenario


admin.site.register(Profile)
admin.site.register(GitHubUser)
admin.site.register(Asm)
admin.site.register(Assembly)
admin.site.register(Scratch)
admin.site.register(CompilerConfig)
admin.site.register(Course)
admin.site.register(CourseChapter)
admin.site.register(CourseScenario)
