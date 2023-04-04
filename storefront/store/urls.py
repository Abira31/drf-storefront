from django.urls import path,include
from .import views
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('products', views.ProducViewSet)
router.register('collections', views.CollectionViewSet)

products_router = routers.NestedSimpleRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet,basename='product-reviews')



urlpatterns = router.urls + products_router.urls

