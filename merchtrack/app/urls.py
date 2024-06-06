from django.conf import settings
from django.views.static import serve
from django.urls import path,re_path, include
from . import views
from .view import product, order, customer, report, collection, fulfillment

urlpatterns = [
    path("", views.home, name='home'),
    # path("trackOrder", views.trackOrder, name='trackOrder'),
    path("aboutUs", views.aboutUs, name='aboutUs'),
    path("contactUs", views.contactUs, name='contactUs'),
    path("order-entry", views.orderEntry, name='order-entry'),
    path('adminTracker', views.adminTracker, name='adminTracker'),
    path('student-info', views.studentInfo, name='student-info'),
    path('registration', views.register, name='registration'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('messages', views.messages, name='messages'),
    path('success', views.success, name='success'),

    path('create-product', product.create_product, name='create_product'),
    path('products', product.product_list, name='product_list'),
    path('edit-product/<int:product_id>/', product.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', product.delete_product, name='delete_product'),

    path('create_order/', order.create_order, name='create_order'),
    path('api/customer_info/', views.customer_info, name='customer_info'),

    path('order_list', order.order_list, name='order_list'),
    path('order_detail/<int:order_id>/', order.order_detail, name='order_detail'),
    path('edit_order/<int:order_id>/', order.edit_order, name='edit_order'),
    path('delete_order/<int:order_id>/', order.delete_order, name='delete_order'),
    path('sales_report', order.sales_report, name='sales_report'),

    path('reports/', report.report_index, name='reports'),

    path('reports/orders/', report.order_report, name='order_report'),
    path('reports/products/', report.product_report, name='product_report'),
    path('reports/products/<int:product_id>/', report.product_report, name='product_report'),
    # path('reports/customers/<int:customer_id>/', report.customer_report, name='customer_report'),
    path('reports/customers/', report.customer_report, name='customer_report'),


    path('reports/sales/', report.sales_report, name='sales_report'),
    path('reports/fulfillment/', report.fulfillment_report, name='fulfillment_report'),
    path('api/sales_data/<int:product_id>/', report.sales_data_api, name='sales_data_api'),
    path('reports/survey/', report.survey_report, name='survey_report'),
    path('reports/collections/', report.collections_report, name='collections_report'),
    path('reports/logs/', report.log_report, name='log_report'),


    path('customers/', customer.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', customer.customer_detail, name='customer_detail'),
    path('customers/edit/<int:customer_id>/', customer.edit_customer, name='edit_customer'),


    path('collections/', collection.collections_index, name='collections_index'),
    path('collections/<int:order_id>/', collection.collection_detail, name='collection_detail'),
    path('customer_payment/', collection.customer_payment, name='customer_payment'),
    path('customer_payment/<int:order_id>/', collection.customer_make_payment, name='customer_make_payment'),


    path('fulfillment/', fulfillment.fulfillment_view, name='fulfillment_view'),
    path('survey/<int:order_id>/', views.survey_view, name='survey_view'),
    path('survey/thank-you/', views.survey_thank_you, name='survey_thank_you'),


    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^.*$', views.not_found, name='404'),
]