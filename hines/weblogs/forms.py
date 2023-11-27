from django import forms


class ManualSubmitWebmentionForm(forms.Form):
    """
    The same as https://github.com/beatonma/django-wm/blob/master/mentions/forms/manual_submit_webmention.py
    but with the target being hidden
    """

    target = forms.URLField(label="The URL of my page", widget=forms.HiddenInput())
    source = forms.URLField(
        label="The URL of your page",
        required=True,
        widget=forms.URLInput(
            attrs={"class": "form__control", "placeholder": "https://…"}
        ),
    )
