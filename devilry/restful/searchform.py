from django import forms
import fields


def _create_seachform(cls):
    class SearchForm(forms.Form):
        query = forms.CharField(required=False)
        limit = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=cls._meta.simplified._meta.ordering)
        result_fieldgroups = fields.CharListWithFallbackField()
        search_fieldgroups = fields.CharListWithFallbackField()
    cls.SearchForm = SearchForm
