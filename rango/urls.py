from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('category-list', views.CategoryListView.as_view(), name='category-list'),
    path('category/<slug:category_name_slug>/', views.show_category, name='show_category'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', views.add_page, name='add_page'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('addproduct/', views.ProductAddView.as_view(), name='product-add'),
    path('productlist/', views.ProductListView.as_view(), name='product-list'),
    path('page-detail/<slug:pk>', views.PageDetailView.as_view(), name='page-detail'),
    path('productdetail/<slug:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('likeproduct/<slug:pk>', views.LikeProduct.as_view(), name='product-like'),
    path('likepage/<slug:pk>', views.LikePage.as_view(), name='page-like'),
    path('trending/', views.TrendingView.as_view(), name='trending'),
    path('discovery/', views.DiscoveryView.as_view(), name='discovery'),
    path('bakers/', views.BakersView.as_view(), name='bakers')
]
