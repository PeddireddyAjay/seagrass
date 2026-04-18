from django.urls import path
from .import views

urlpatterns = [

    path('stress_home/', views.stress_home,name="stress_home"),


    path('stress_register/',views.stress_register),
    path('stress_login/',views.stress_login),
    path('stress_logout/', views.stress_logout, name="stress_logout"),


    path('aqua_final_report/', views.aqua_final_report, name="aqua_final_report"),


    path('getkey_stress/<str:project_id>/',views.getkey_stress),
    path('decrypt_data_stress/<str:project_id>/',views.decrypt_data_stress),


    path('stress_scan/',views.stress_scan, name="stress_scan"),
    path('stress_calculation/<str:project_id>/',views.stress_calculation, name="stress_calculation"),
    path('stress_file/',views.stress_file,name="stress_file")


]

# # #