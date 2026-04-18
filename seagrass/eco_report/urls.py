from django.urls import path
from .import views

urlpatterns = [

    path('eco_home/', views.eco_home,name="eco_home"),


    path('eco_register/',views.eco_register),
    path('eco_login/',views.eco_login),
    path('eco_logout/', views.eco_logout, name="eco_logout"),


    path('bio_final_report/', views.bio_final_report, name="bio_final_report"),


    path('getkey_eco/<str:project_id>/',views.getkey_eco),
    path('decrypt_data_eco/<str:project_id>/',views.decrypt_data_eco),


    path('eco_scan/',views.eco_scan, name="eco_scan"),
    path('eco_calculation/<str:project_id>/',views.eco_calculation, name="eco_calculation"),
    path('eco_file/',views.eco_file,name="eco_file")


]

# # #