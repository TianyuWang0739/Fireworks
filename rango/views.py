from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from rango.models import Category, Page, Product, FavoriteProduct, FavoritePage
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm, ProductForm, FilterForm
from datetime import datetime


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    visitor_cookie_handler(request)

    return render(request, 'rango/home.html', context=context_dict)


def about(request):

    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None
    
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    
    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)  # This could be better done; for the purposes of TwD, this is fine. DM.
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'rango/register.html', 
               context={'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    
    request.session['visits'] = visits


class CategoryListView(ListView):
    queryset = Category.objects.all()
    template_name = 'rango/category-list.html'


class Profile(TemplateView):
    template_name = 'rango/profile.html'


class ProductAddView(LoginRequiredMixin, CreateView):
    model = Product
    form = ProductForm
    template_name = 'rango/product-add.html'
    fields = '__all__'


class ProductListView(FormMixin, ListView):
    model = Product
    template_name = 'rango/product-list.html'
    form_class = FilterForm

    def get_queryset(self):
        queryset = super(ProductListView, self).get_queryset()
        form = self.get_form()
        if form.is_valid():
            data = form.cleaned_data
            data = {k: v for k, v in data.items() if v}
            queryset = queryset.filter(**data)

        q = self.request.GET.get('q')
        if q is not None:
            queryset = queryset.filter(name__icontains=q)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        form = self.get_form()

        context['form'] = form
        return context

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        kwargs.update({
            'data': self.request.GET,
        })
        return kwargs


class PageDetailView(DetailView):
    model = Page
    template_name = 'rango/page-detail.html'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'rango/product-detail.html'


class LikeProduct(LoginRequiredMixin, SingleObjectMixin, View):
    model = Product

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        FavoriteProduct.objects.create(product=obj, user=request.user)
        return redirect('rango:product-detail', pk=obj.pk)


class LikePage(LoginRequiredMixin, SingleObjectMixin, View):
    model = Page

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        FavoritePage.objects.create(page=obj, user=request.user)
        return redirect('/')


class TrendingView(TemplateView):
    template_name = 'rango/trending.html'


class DiscoveryView(TemplateView):
    template_name = 'rango/discovery.html'


class BakersView(TemplateView):
    template_name = 'rango/bakers.html'
