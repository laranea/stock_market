from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.forms.models import inlineformset_factory
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView

from .forms import UserForm
from .models import UserProfile


# Create your views here.
class home(TemplateView):
    template_name = 'home.html'

class about(TemplateView):
    template_name = 'about.html'


class userProfile(TemplateView):
    template_name = 'profile.html'

    @login_required
    def userProfile(request):
        user = request.user
        context = {'user': user}
        return render(request, template_name, context)


@login_required()  # only logged in users should access this
def edit_user(request):
    pk = request.user.pk
    # querying the User object with pk from url
    user = User.objects.get(pk=pk)

    # prepopulate UserProfileForm with retrieved user values from above.
    user_form = UserForm(instance=user)

    # The sorcery begins from here, see explanation below
    ProfileInlineFormset = inlineformset_factory(User, UserProfile,
                                                 fields=('photo', 'website', 'bio', 'phone', 'city', 'country', 'organization'))
    formset = ProfileInlineFormset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = UserForm(request.POST, request.FILES, instance=user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return HttpResponseRedirect('/profile/')

        return render(request, "account/profile_edit.html", {
            "noodle": pk,
            "noodle_form": user_form,
            "formset": formset,
        })
    else:
        raise PermissionDenied
