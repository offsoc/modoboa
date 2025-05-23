"""OVH SMS backend."""

import ovh

from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from . import SMSBackend


class OVHBackend(SMSBackend):
    """OVH SMS backend class."""

    settings = {
        "sms_ovh_endpoint": {
            "type": forms.ChoiceField,
            "attrs": {
                "label": _("API endpoint"),
                "initial": "ovh-eu",
                "choices": (
                    ("ovh-eu", _("OVH Europe")),
                    ("ovh-us", _("OVH US")),
                    ("ovh-ca", _("OVH North-America")),
                    ("soyoustart-eu", _("So you Start Europe")),
                    ("soyoustart-ca", _("So you Start North America")),
                    ("kimsufi-eu", _("Kimsufi Europe")),
                    ("kimsufi-ca", _("Kimsufi North America")),
                ),
            },
        },
        "sms_ovh_application_key": {
            "type": forms.CharField,
            "attrs": {"label": _("Application key"), "required": False},
        },
        "sms_ovh_application_secret": {
            "type": forms.CharField,
            "attrs": {
                "label": _("Application secret"),
                "widget": forms.widgets.PasswordInput(render_value=True),
                "required": False,
            },
        },
        "sms_ovh_consumer_key": {
            "type": forms.CharField,
            "attrs": {
                "label": _("Consumer key"),
                "widget": forms.widgets.PasswordInput(render_value=True),
                "required": False,
            },
        },
    }

    serializer_settings = {
        "sms_ovh_endpoint": {
            "type": serializers.ChoiceField,
            "attrs": {
                "default": "ovh-eu",
                "choices": (
                    ("ovh-eu", _("OVH Europe")),
                    ("ovh-us", _("OVH US")),
                    ("ovh-ca", _("OVH North-America")),
                    ("soyoustart-eu", _("So you Start Europe")),
                    ("soyoustart-ca", _("So you Start North America")),
                    ("kimsufi-eu", _("Kimsufi Europe")),
                    ("kimsufi-ca", _("Kimsufi North America")),
                ),
            },
        },
        "sms_ovh_application_key": {
            "type": serializers.CharField,
            "attrs": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        },
        "sms_ovh_application_secret": {
            "type": serializers.CharField,
            "attrs": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        },
        "sms_ovh_consumer_key": {
            "type": serializers.CharField,
            "attrs": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        },
    }

    structure = [
        (
            "sms_ovh_endpoint",
            {
                "label": _("API endpoint"),
                "display": "sms_password_recovery=true&sms_provider=ovh",
            },
        ),
        (
            "sms_ovh_application_key",
            {
                "label": _("Application key"),
                "display": "sms_password_recovery=true&sms_provider=ovh",
            },
        ),
        (
            "sms_ovh_application_secret",
            {
                "label": _("Appication secret"),
                "display": "sms_password_recovery=true&sms_provider=ovh",
                "password": True,
            },
        ),
        (
            "sms_ovh_consumer_key",
            {
                "label": _("Consumer key"),
                "display": "sms_password_recovery=true&sms_provider=ovh",
                "password": True,
            },
        ),
    ]

    visibility_rules = {
        "sms_ovh_endpoint": "sms_provider=ovh",
        "sms_ovh_application_key": "sms_provider=ovh",
        "sms_ovh_application_secret": "sms_provider=ovh",
        "sms_ovh_consumer_key": "sms_provider=ovh",
    }

    @cached_property
    def client(self):
        return ovh.Client(
            endpoint=self._params.get_value("sms_ovh_endpoint"),
            application_key=self._params.get_value("sms_ovh_application_key"),
            application_secret=self._params.get_value("sms_ovh_application_secret"),
            consumer_key=self._params.get_value("sms_ovh_consumer_key"),
        )

    def send(self, text, recipients):
        """Send a new SMS to given recipients."""
        services = self.client.get("/sms")
        result = self.client.post(
            f"/sms/{services[0]}/jobs",
            message=text,
            receivers=recipients,
            priority="high",
            noStopClause=True,
            senderForResponse=True,
        )
        if result["totalCreditsRemoved"] != len(recipients):
            return False
        return True
