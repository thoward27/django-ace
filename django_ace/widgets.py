from __future__ import unicode_literals

from typing import final

from django import forms

try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt

from django.conf import settings
from django.utils.safestring import mark_safe


@final
class AceWidget(forms.Textarea):
    def __init__(
        self,
        mode: str="markdown",
        theme: str="dracula",
        wordwrap: bool=True,
        width: str="100%",
        height: str="300px",
        showprintmargin: bool=False,
        showinvisibles: bool=False,
        usesofttabs: bool=True,
        maxlines: str | None=None,
        toolbar: bool=True,
        extensions: list[str] | None=None,
        options: dict[str, str] | None=None,
        *args,
        **kwargs
    ):
        self.mode = mode
        self.theme = theme
        self.wordwrap = wordwrap
        self.width = width
        self.height = height
        self.maxlines = maxlines
        self.showprintmargin = showprintmargin
        self.showinvisibles = showinvisibles
        self.toolbar = toolbar
        self.usesofttabs = usesofttabs
        self.extensions = extensions
        self.aceoptions: dict[str, str] = (options or {}) | getattr(settings, "DJANGOACE_DEFAULT_ACE_OPTIONS", {})
        super(AceWidget, self).__init__(*args, **kwargs)

    @property
    def media(self):
        js = ["django_ace/ace/ace.js", "django_ace/widget.js"]

        if self.mode:
            js.append("django_ace/ace/mode-%s.js" % self.mode)
        if self.theme:
            js.append("django_ace/ace/theme-%s.js" % self.theme)
        if self.extensions:
            for extension in self.extensions:
                js.append("django_ace/ace/ext-%s.js" % extension)

        css = {"screen": ["django_ace/widget.css"]}

        return forms.Media(js=js, css=css)

    def render(self, name: str, value: str, attrs: dict[str, str | bool] | None=None, renderer=None) -> str:
        attrs = attrs or {}

        ace_attrs = {
            "class": "django-ace-widget loading",
            "style": "width:%s; height:%s" % (self.width, self.height),
        }

        if self.mode:
            ace_attrs["data-mode"] = self.mode
        if self.theme:
            ace_attrs["data-theme"] = self.theme
        if self.wordwrap:
            ace_attrs["data-wordwrap"] = "true"
        if self.maxlines:
            ace_attrs["data-maxlines"] = str(self.maxlines)

        if self.aceoptions:
            ace_attrs |= {f"data-aceoption-{k}": v for k, v in self.aceoptions.items()}

        ace_attrs["data-showprintmargin"] = "true" if self.showprintmargin else "false"
        ace_attrs["data-showinvisibles"] = "true" if self.showinvisibles else "false"
        ace_attrs["data-usesofttabs"] = "true" if self.usesofttabs else "false"

        textarea = super(AceWidget, self).render(name, value, attrs, renderer)

        html = "<div{}><div></div></div>{}".format(flatatt(ace_attrs), textarea)

        if self.toolbar:
            toolbar = (
                '<div style="width: {}" class="django-ace-toolbar">'
                '<a href="./" class="django-ace-max_min"></a>'
                "</div>"
            ).format(self.width)
            html = toolbar + html

        html = '<div class="django-ace-editor">{}</div>'.format(html)
        return mark_safe(html)
