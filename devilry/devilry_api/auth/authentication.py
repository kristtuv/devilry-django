# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy
from rest_framework import authentication

from devilry.devilry_api.models import APIKey


class TokenAuthentication(authentication.TokenAuthentication):
    model = APIKey

    def authenticate(self, request):
        """
        Sets the token that is used to authenticate to our request object.
        """
        retval = super(TokenAuthentication, self).authenticate(request)
        if retval is None:
            request.apikey_token = None
            return None
        request.apikey_token = retval[1]
        return retval

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise authentication.exceptions.AuthenticationFailed(ugettext_lazy('Invalid token.'))

        if not token.user.is_active:
            raise authentication.exceptions.AuthenticationFailed(ugettext_lazy('User inactive or deleted.'))

        if token.has_expired:
            raise authentication.exceptions.AuthenticationFailed(ugettext_lazy('Api key has expired.'))

        return (token.user, token)


class SessionAuthentication(authentication.SessionAuthentication):
    pass