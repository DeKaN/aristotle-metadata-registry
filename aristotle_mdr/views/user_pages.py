import datetime

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin, UserPassesTestMixin
from django.apps import apps
from django.contrib.auth.views import login
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView, UpdateView
from reversion.models import Revision

from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR
from aristotle_mdr.utils import fetch_aristotle_settings
from aristotle_mdr.views.utils import paginate_sort_opts, paginate_workgroup_sort_opts


def friendly_redirect_login(request):
    if request.user.is_authenticated():
        return redirect(request.GET.get('next', reverse('aristotle:userHome')))
    return login(request)


def _get_cached_query_count(qs, key, ttl):
    count = cache.get(key, None)
    if not count:
        count = qs.count()
        cache.set(key, count, ttl)
    return count


def _model_to_cache_key(model_type):
    return 'aristotle_adminpage_object_count_%s_%s' % (model_type.app_label, model_type.model)


def _get_cached_object_count(model_type):
    CACHE_KEY = _model_to_cache_key(model_type)
    query = model_type.model_class().objects
    return _get_cached_query_count(query, CACHE_KEY, 60 * 60 * 12)  # Cache for 12 hours


# Can be extracted and used in other classes
class RegistrarRequiredMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self, user):
        return user.profile.is_registrar


class UserContextMixin(object):
    def get_context_data(self, **kwargs):
        kwargs.update({
            'item': self.request.user,
        })
        return super(UserContextMixin, self).get_context_data(**kwargs)


class HomeView(LoginRequiredMixin, UserContextMixin, TemplateView):
    template_name = 'aristotle_mdr/user/userHome.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'recent': Revision.objects.filter(user=self.request.user).order_by('-date_created')[:10]
        })
        return super(HomeView, self).get_context_data(**kwargs)


class RolesView(LoginRequiredMixin, UserContextMixin, TemplateView):
    template_name = 'aristotle_mdr/user/userRoles.html'


class RecentView(LoginRequiredMixin, ListView):
    template_name = 'aristotle_mdr/user/recent.html'

    def get_paginate_by(self, queryset):
        return self.request.GET.get('pp', 20)

    def get_queryset(self):
        return Revision.objects.filter(user=self.request.user).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super(RecentView, self).get_context_data(**kwargs)
        context['page'] = context.get('page_obj')  # dirty hack for current template
        return context


class InboxView(LoginRequiredMixin, UserContextMixin, TemplateView):
    template_name = 'aristotle_mdr/user/userInbox.html'

    def get_context_data(self, **kwargs):
        folder = self.kwargs.get('folder', 'unread')
        notices = self.request.user.notifications
        if folder == 'unread':
            notices = notices.unread()
        kwargs.update({
            'notifications': notices.all(),
            'folder': folder
        })
        return super(InboxView, self).get_context_data(**kwargs)


class AdminToolsView(LoginRequiredMixin, SuperuserRequiredMixin, UserContextMixin, DetailView):
    template_name = 'aristotle_mdr/user/userAdminTools.html'
    context_object_name = 'models'

    def get_object(self, queryset=None):
        aristotle_apps = fetch_aristotle_settings().get('CONTENT_EXTENSIONS', []) + ["aristotle_mdr"]
        models = ContentType.objects.filter(app_label__in=aristotle_apps).all()
        model_stats = {}
        for m in models:
            if m.model_class() and issubclass(m.model_class(), MDR._concept) and not m.model.startswith("_"):
                # Only output subclasses of 11179 concept
                app_models = model_stats.get(m.app_label, {'app': None, 'models': []})
                if app_models['app'] is None:
                    app_models['app'] = getattr(apps.get_app_config(m.app_label), 'verbose_name')
                app_models['models'].append(
                    (
                        m.model_class(),
                        _get_cached_object_count(m),
                        reverse("admin:%s_%s_changelist" % (m.app_label, m.model))
                    )
                )
                model_stats[m.app_label] = app_models
        return model_stats


class AdminStatsView(LoginRequiredMixin, SuperuserRequiredMixin, UserContextMixin, DetailView):
    template_name = 'aristotle_mdr/user/userAdminStats.html'
    context_object_name = 'model_stats'
    mod_counts = None

    def get_context_data(self, **kwargs):
        kwargs.update({
            'model_max': max(self.mod_counts)
        })
        return super(AdminStatsView, self).get_context_data(**kwargs)

    def get_object(self, queryset=None):
        aristotle_apps = fetch_aristotle_settings().get('CONTENT_EXTENSIONS', []) + ["aristotle_mdr"]
        models = ContentType.objects.filter(app_label__in=aristotle_apps).all()
        model_stats = {}

        # Get datetime objects for '7 days ago' and '30 days ago'
        t7 = datetime.date.today() - datetime.timedelta(days=7)
        t30 = datetime.date.today() - datetime.timedelta(days=30)
        self.mod_counts = []  # used to get the maximum count

        use_cache = True  # We still cache but its much, much shorter
        for m in models:
            if m.model_class() and issubclass(m.model_class(), MDR._concept) and not m.model.startswith("_"):
                # Only output subclasses of 11179 concept
                app_models = model_stats.get(m.app_label, {'app': None, 'models': []})
                if app_models['app'] is None:
                    app_models['app'] = getattr(apps.get_app_config(m.app_label), 'verbose_name')
                if use_cache:
                    total = _get_cached_query_count(
                        qs=m.model_class().objects,
                        key=_model_to_cache_key(m) + "__all_time",
                        ttl=60
                    )
                    t7_val = _get_cached_query_count(
                        qs=m.model_class().objects.filter(created__gte=t7),
                        key=_model_to_cache_key(m) + "__t7",
                        ttl=60
                    )
                    t30_val = _get_cached_query_count(
                        qs=m.model_class().objects.filter(created__gte=t30),
                        key=_model_to_cache_key(m) + "__t30",
                        ttl=60
                    )
                else:
                    total = m.model_class().objects.count()
                    t7_val = m.model_class().objects.filter(created__gte=t7).count()
                    t30_val = m.model_class().objects.filter(created__gte=t30).count()

                self.mod_counts.append(total)
                app_models['models'].append(
                    (
                        m.model_class(),
                        {
                            'all_time': total,
                            't7': t7_val,
                            't30': t30_val
                        },
                        reverse("admin:%s_%s_changelist" % (m.app_label, m.model))
                    )
                )
                model_stats[m.app_label] = app_models
        return model_stats


class EditView(LoginRequiredMixin, UpdateView):
    template_name = 'aristotle_mdr/user/userEdit.html'
    form_class = MDRForms.UserSelfEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("aristotle:userHome")


class FavouritesView(LoginRequiredMixin, ListView):
    template_name = 'aristotle_mdr/user/userFavourites.html'

    def get_paginate_by(self, queryset):
        return self.request.GET.get('pp', 20)

    def get_queryset(self):
        return self.request.user.profile.favourites.select_subclasses()

    def get_context_data(self, **kwargs):
        kwargs.update({
            'help': self.request.GET.get('help', False),
            'favourite': self.request.GET.get('favourite', False),
            'select_all_list_queryset_filter': 'favourited_by__user=user'  # no information leakage here.
        })
        return super(FavouritesView, self).get_context_data(**kwargs)


class RegistrarToolsView(LoginRequiredMixin, RegistrarRequiredMixin, TemplateView):
    template_name = 'aristotle_mdr/user/userRegistrarTools.html'


class ReviewListView(LoginRequiredMixin, RegistrarRequiredMixin, ListView):
    template_name = 'aristotle_mdr/user/userReviewList.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        authorities = [i[0] for i in self.request.user.profile.registrarAuthorities.all().values_list('id')]

        # Registars can see items they have been asked to review
        q = Q(Q(registration_authority__id__in=authorities) & ~Q(status=MDR.REVIEW_STATES.cancelled))

        return MDR.ReviewRequest.objects.visible(self.request.user).filter(q)

    def get_context_data(self, **kwargs):
        context = super(ReviewListView, self).get_context_data(**kwargs)
        context['page'] = context.get('page_obj')  # dirty hack for current template
        return context


class MyReviewListView(LoginRequiredMixin, ListView):
    template_name = 'aristotle_mdr/user/my_review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        # Users can see any items they have been asked to review
        q = Q(requester=self.request.user)
        return MDR.ReviewRequest.objects.visible(self.request.user).filter(q)

    def get_context_data(self, **kwargs):
        context = super(MyReviewListView, self).get_context_data(**kwargs)
        context['page'] = context.get('page_obj')  # dirty hack for current template
        return context


class DjangoAdminWrapperView(LoginRequiredMixin, TemplateView):
    template_name = 'aristotle_mdr/user/admin.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'page_url': self.args[0]
        })
        return super(DjangoAdminWrapperView, self).get_context_data(**kwargs)


class ReviewDetailsView(LoginRequiredMixin, DetailView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/user/request_review_details.html"
    context_object_name = "review"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReviewDetailsView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', reverse('aristotle:userReadyForReview'))
        return context

    def get_queryset(self):
        return MDR.ReviewRequest.objects.visible(self.request.user)


class CreatedItemsListView(LoginRequiredMixin, ListView):
    paginate_by = 25
    template_name = "aristotle_mdr/user/sandbox.html"
    sort_by = None

    def get_queryset(self, *args, **kwargs):
        self.sort_by = self.request.GET.get('sort', 'name_asc')
        if self.sort_by not in paginate_sort_opts.keys():
            self.sort_by = 'name_asc'

        return MDR._concept.objects.filter(
            Q(
                submitter=self.request.user,
                statuses__isnull=True
            ) & Q(
                Q(review_requests__isnull=True) | Q(review_requests__status=MDR.REVIEW_STATES.cancelled)
            )
        ).order_by(*paginate_sort_opts.get(self.sort_by))

    def get_context_data(self, **kwargs):
        kwargs.update({
            'sort': self.sort_by
        })
        return super(CreatedItemsListView, self).get_context_data(**kwargs)


class WorkgroupsView(LoginRequiredMixin, ListView):
    template_name = 'aristotle_mdr/user/userWorkgroups.html'
    sort_by = None
    text_filter = None

    def get_paginate_by(self, queryset):
        return self.request.GET.get('pp', 20)

    def get_workgroups(self):
        return self.request.user.profile.myWorkgroups

    def get_queryset(self):
        self.sort_by = self.request.GET.get('sort', 'name_desc')
        self.text_filter = self.request.GET.get('filter', '')
        qs = self.get_workgroups()
        if self.text_filter:
            qs = qs.filter(
                Q(name__icontains=self.text_filter) | Q(definition__icontains=self.text_filter)
            )

        try:
            sorter, direction = self.sort_by.split('_')
            if sorter not in paginate_workgroup_sort_opts.keys():
                sorter = 'name'
                self.sort_by = "name_desc"
            direction = {'asc': '', 'desc': '-'}.get(direction, '')
        except:
            self.sort_by = 'name'
            sorter, direction = 'name', ''

        opts = paginate_workgroup_sort_opts.get(sorter)

        try:
            sort_field, extra = opts
            qs = extra(qs)
        except:
            sort_field = opts
        qs = qs.order_by(direction + sort_field)
        return qs

    def get_context_data(self, **kwargs):
        kwargs.update({
            'sort': self.sort_by,
            'filter': self.text_filter
        })
        context = super(WorkgroupsView, self).get_context_data(**kwargs)
        context['page'] = context.get('page_obj')  # dirty hack for current template
        return context


class ArchivedWorkkgroupsView(WorkgroupsView):
    template_name = 'aristotle_mdr/user/userWorkgroupArchives.html'

    def get_workgroups(self):
        return self.request.user.profile.workgroups.filter(archived=True)
