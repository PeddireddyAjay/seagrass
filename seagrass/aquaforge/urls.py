from django.urls import path
from .import views

urlpatterns = [

    path('aqua_home/', views.aqua_home,name="aqua_home"),


    path('aqua_register/',views.aqua_register),
    path('aqua_login/',views.aqua_login),
    path('aqua_logout/', views.aqua_logout, name="aqua_logout"),


    path('ad_min_protocols/', views.ad_min_protocols, name="ad_min_protocols"),


    path('getkey_aqua/<str:project_id>/',views.getkey_aqua),
    path('decrypt_data_aqua/<str:project_id>/',views.decrypt_data_aqua),


    path('aqua_scan/',views.aqua_scan, name="aqua_scan"),
    path('aqua_calculation/<str:project_id>/',views.aqua_calculation, name="aqua_calculation"),
    path('aqua_file/',views.aqua_file,name="aqua_file")


]

