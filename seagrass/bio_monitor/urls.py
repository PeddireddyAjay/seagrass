from django.urls import path
from .import views

urlpatterns = [

    path('bio_home/', views.bio_home,name="bio_home"),


    path('bio_register/',views.bio_register),
    path('bio_login/',views.bio_login),
    path('bio_logout/', views.bio_logout, name="bio_logout"),


    path('stress_final_report/', views.stress_final_report, name="stress_final_report"),


    path('getkey_bio/<str:project_id>/',views.getkey_bio),
    path('decrypt_data_bio/<str:project_id>/',views.decrypt_data_bio),


    path('bio_scan/',views.bio_scan, name="bio_scan"),
    path('bio_calculation/<str:project_id>/',views.bio_calculation, name="bio_calculation"),
    path('bio_file/',views.bio_file,name="bio_file")


]

# # #