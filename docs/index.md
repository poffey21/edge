Welcome to {{ project_name }}!
==============================

```
#Windows
django-admin startproject --template=https://github.com/poffey21/edge/archive/master.zip -e=py -e=env -e=bat -e=ps1 -n=README.md demo
cp ./local.env ./demo/src/demo/settings/
cd demo
git init .
git add .
git commit -m "initial commit"
git log  # the SHA-1 Hash of name/size/text of every file
git branch create-chat-app
git checkout create-chat-app
scripts/local_enable.ps1
python manage.py test
python manage.py migrate
python manage.py runserver
python manage.py startapp chat

rm chat/admin.py
git add .
git commit -m "added files created by startapp"
git log

git add .
git commit -m "updated tests directory to separate views and models"
git log
```

### Add app to `demo/settings/base.py`

```
'chat',
```

### Add model to chat/models.py

```
class Message(models.Model):
    """ A basic message with a body and a user"""

    user_id = models.CharField(max_length=32)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
```

```
python manage.py makemigrations
git status
git add .
git commit -m "created model for message"
git log
```

##### Test model

`tests/test_models.py`

```
from django.urls import reverse

from . import models


class MessageTestCase(TestCase):
    """Quick and simple unit tests for Message Model"""

    def test_creation_of_message(self):
        """ Let's make sure we can create a message """
        obj = models.Message.objects.create(
            user_id='DL12924',
            message='This is a new message'
        )
        self.assertEqual(obj.message, u'This is a new message')

    def test_ordering_of_messages(self):
        """ Let's see if the order is correct """
        for i in range(99):
            models.Message.objects.create(
                user_id='DL12924',
                message='This is a new message'
            )
        last_message = models.Message.objects.create(
            user_id='DL12924',
            message='This is the newest message'
        )
        self.assertEqual(100, models.Message.objects.count())
        self.assertEqual(last_message, models.Message.objects.all().last())
```

`demo/settings/development.py`

```
`'--cover-package=chat',
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

{% block title %}Chat Session{% endblock %}

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

### Add View Tests to `chat/tests.py`

```
    def test_new_subscription_page(self):
        response = self.client.post(
            reverse('chat:chat-session'),
            {'user_id': ('d' * 8), 'message': 'this is a new message'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='chat/message_form.html')
```


###################################################

add putty 80:localhost:8100

```
git clone https://github.com/poffey21/demo.git 8100
cp local.env 8100/src/demo/settings
export DJANGO_SETTINGS_MODULE=demo.settings.production
cd 8100/src
python manage.py migrate
python manage.py collectstatic
cd -
uwsgi --ini demo.ini
```

###################################################

