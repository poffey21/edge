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
    timestamp = models.DateTimeField(auto_now_add=True)=

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

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(MessageView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.all()
        return context
```


Add URLs.py to `chat/urls.py`

```
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^/$', views.MessageView.as_view(), name='chat-window'),
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
