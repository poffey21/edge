Welcome to {{ project_name }}!
==============================

```
django-admin startproject --template=https://github.com/poffey21/edge/archive/master.zip -e=py -e=md -e=env -e=bat -e=ps1 demo
cp .\local.env .\demo\src\demo\settings\
cd demo
git init .
git add .
git commit -m "initial commit"
git branch create-chat-app
git checkout create-chat-app
scripts\local_enable.ps1
python manage.py test
python manage.py migrate
python manage.py runserver
python manage.py startapp chat


```

### Add app to `demo/settings/base.py`

```
'chat',
```

### Add model to chat/modes.py

```
class Message(models.Model):
    """ A basic message with a body and a user"""

    user_id = models.CharField(max_length=32)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
```

### Add view to chatops/views.py

```
from django.views import generic

from . import models


class MessageView(generic.CreateView):
    model = models.Message
    fields = ['user_id', 'message']

    def get_initial(self):
        initial = self.initial.copy()
        user_id = self.request.session.get('user_id', None)
        if user_id:
            initial['user_id'] = user_id
        return initial

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['user_id'] = self.object.user_id
        return super(MessageView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(MessageView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.all()
        return context
```

Add Template to `chat/templates/message_form.html`

```
{% extends '200.html' %}

{% block content %}
We are in the chat window.
<form  class="form" action="{{ url }}" method="post">
    {% csrf_token %}
    {{ form }}
    <button type="submit" class="btn btn-{{ button_class|default:'default' }}">{{ button_message|default:'Submit' }}</button>
</form>

<ul class="list-group">
{% for obj in object_list %}
    <li class="list-group-item"><span class="label label-primary">{{ obj.user_id }}</span>{{ obj.message }}</li>
{% endfor %}
</ul>
{% endblock content %}
```


Add URLs.py to `chat/urls.py`

```
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MessageView.as_view(), name='chat-session'),
]
```

Add URL to `demo/urls.py`

```
url(r'^chat/', include('chat.urls', namespace='chat')),
```

Add menu item to `demo/context_processors.py`

```
    {
        'title': 'Chat',
        'url': determine_url('chat:chat-session'),
    },
```

