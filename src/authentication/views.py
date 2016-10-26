from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.views import generic

from . import models


class UserIDRequiredMixin(object):

    @method_decorator(login_required(login_url=reverse_lazy('account:login')))
    def dispatch(self, request, *args, **kwargs):
        return super(UserIDRequiredMixin, self).dispatch(request, *args, **kwargs)

class Logout(generic.View):

    def get(self, *args, **kwargs):
        logout(self.request)
        return HttpResponseRedirect('/')

class GroupAssociationsListView(UserIDRequiredMixin, generic.ListView):
    model = Group
    template_name = 'authentication/user_group_list.html'

    def get_queryset(self):
        qs = super(GroupAssociationsListView, self).get_queryset()
        return qs.prefetch_related('user_set').order_by('name')


class Profile(UserIDRequiredMixin, generic.DetailView):
    model = get_user_model()
    template_name = 'authentication/profile.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=self.request.user.pk)
        except queryset.model.DoesNotExist as e:
            raise Http404("No MyModel matches the given query.")


class GenerateApiKey(UserIDRequiredMixin, generic.CreateView):
    model = models.Token
    fields = []
    template_name = 'ajax_form.html'

    def get_context_data(self, **kwargs):
        context = super(GenerateApiKey, self). get_context_data(**kwargs)
        context['button_message'] = 'Generate API Key'
        context['url'] = '{}?next={}'.format(self.request.path, self.request.GET.get('next', reverse_lazy('account:profile')))
        return context

    def form_valid(self, form):
        user = self.request.user
        api = self.model.objects.get_or_create(user=user)[0]
        api_key = api.generate_api_key()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            format_html(
                'Your API Key is now set to: <input class="form-control" type="text" value="{}" readonly>',
                api_key
            )
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return unquote(self.request.GET.get('next', '/'))


class SetSessionUser(generic.View):
    """ This is for administrators and possibly could be used behind a Access Management Cookie """
    def get(self, *args, **kwargs):
        next_url = self.request.GET.get('next', '/')
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.ERROR, 'You are not allowed to use this feature.')
            return HttpResponseRedirect(next_url)
        user_id = self.request.GET.get('user_id')
        if self.request.user and user_id != self.request.user.id:
            logout(self.request)
        new_user = authenticate(username=user_id)
        if new_user:
            login(
                self.request,
                new_user,
                backend='django.contrib.auth.backends.ModelBackend',
            )
        else:
            messages.add_message(self.request, messages.ERROR, 'Unable to login as different user. Authenticate stage failed')
        return HttpResponseRedirect(next_url)
