from platform import platform
from typing import Any, Dict, Optional, TYPE_CHECKING

from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers
from rest_framework.reverse import reverse

from .middleware import Request
from .models.github import GitHubUser

from .models.profile import Profile
from .models.scratch import Scratch


def serialize_profile(
    request: Request, profile: Profile, small: bool = False
) -> Dict[str, Any]:
    if profile.user is None:
        return {
            "url": None,
            "html_url": None,
            "is_you": profile == request.profile,  # TODO(#245): remove
            "is_anonymous": True,
            "id": profile.id,
            "is_online": profile.is_online(),
            "is_admin": False,
            "username": f"{profile.pseudonym} (anon)",
            "frog_color": profile.get_frog_color(),
        }
    else:
        user = profile.user

        github: Optional[GitHubUser] = GitHubUser.objects.filter(user=user).first()
        github_details = github.details() if github else None

        small_obj = {
            "url": reverse("user-detail", args=[user.username], request=request),
            "html_url": profile.get_html_url(),
            "is_you": user == request.user,  # TODO(#245): remove
            "is_anonymous": False,
            "id": profile.id,
            "is_online": profile.is_online(),
            "is_admin": user.is_staff,
            "username": user.username,
            "avatar_url": github_details.avatar_url if github_details else None,
        }

        if small:
            return small_obj

        return {
            **small_obj,
            "email": user.email,
            "name": github_details.name if github_details else user.username,
            "github_api_url": github_details.url if github_details else None,
            "github_html_url": github_details.html_url if github_details else None,
        }


if TYPE_CHECKING:
    ProfileFieldBaseClass = serializers.RelatedField[Profile, str, Dict[str, Any]]
else:
    ProfileFieldBaseClass = serializers.RelatedField


class ProfileField(ProfileFieldBaseClass):
    def to_representation(self, profile: Profile) -> Dict[str, Any]:
        return serialize_profile(self.context["request"], profile)


class TerseProfileField(ProfileField):
    def to_representation(self, profile: Profile) -> Dict[str, Any]:
        return serialize_profile(self.context["request"], profile, small=True)


class UrlField(serializers.HyperlinkedIdentityField):
    """
    Read-only field that takes the value returned by the model's get_url method.
    get_url should return a path relative to API_BASE that can be used to retrieve the model from the API.
    """

    def __init__(self, **kwargs: Any):
        kwargs["view_name"] = "__unused__"
        self.target_field = kwargs.pop("target_field", "")
        super().__init__(**kwargs)

    def get_url(
        self, value: Any, view_name: str, request: Any, format: Any
    ) -> Optional[str]:
        if self.target_field:
            value = getattr(value, self.target_field)
        if not value:
            return None
        if hasattr(value, "get_url"):
            return value.get_url()

        raise ImproperlyConfigured("UrlField does not support this type of model")


class HtmlUrlField(UrlField):
    """
    Read-only field that takes the value returned by the model's get_html_url method.
    get_html_url should return a path relative to the frontend that can be used to look at the HTML page for the model.
    """

    def get_url(self, value: Any, view_name: str, request: Any, format: Any) -> str:
        if hasattr(value, "get_html_url"):
            return value.get_html_url()

        raise ImproperlyConfigured("HtmlUrlField does not support this type of model")


class ScratchCreateSerializer(serializers.Serializer[None]):
    name = serializers.CharField(allow_blank=True, required=False)
    compiler = serializers.CharField(allow_blank=True, required=True)
    platform = serializers.CharField(allow_blank=True, required=False)
    compiler_flags = serializers.CharField(allow_blank=True, required=False)
    diff_flags = serializers.JSONField(required=False)
    preset = serializers.CharField(allow_blank=True, required=False)
    source_code = serializers.CharField(allow_blank=True, required=False)
    target_asm = serializers.CharField(allow_blank=True)
    context = serializers.CharField(allow_blank=True)  # type: ignore
    diff_label = serializers.CharField(allow_blank=True, required=False)


class ScratchSerializer(serializers.HyperlinkedModelSerializer):
    slug = serializers.SlugField(read_only=True)
    url = UrlField()
    html_url = HtmlUrlField()
    parent = UrlField(target_field="parent")  # type: ignore
    owner = ProfileField(read_only=True)
    source_code = serializers.CharField(allow_blank=True, trim_whitespace=False)
    context = serializers.CharField(allow_blank=True, trim_whitespace=False)  # type: ignore

    class Meta:
        model = Scratch
        exclude = ["target_assembly"]
        read_only_fields = [
            "url",
            "html_url",
            "parent",
            "owner",
            "last_updated",
            "creation_time",
            "platform",
        ]


class TerseScratchSerializer(ScratchSerializer):
    owner = TerseProfileField(read_only=True)

    class Meta:
        model = Scratch
        fields = [
            "url",
            "html_url",
            "slug",
            "owner",
            "last_updated",
            "creation_time",
            "platform",
            "compiler",
            "name",
            "score",
            "max_score",
            "parent",
        ]
