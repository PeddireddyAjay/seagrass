from django.contrib import messages
from django.shortcuts import render,redirect
from ad_min.models import seagrass,hydra
from django.core.mail import send_mail

# Create your views here.

# homepage.......

def home(request):
    return render(request,'homepage/homepage.html')

# # admin login & logout

def adminlogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if email == "admin@gmail.com" and password == "admin":
            messages.info(request,"Admin Login Successful")
            return redirect("/adminhome/")
        else:
            messages.error(request,"wrong credentials")
            return render(request, 'ad_min/admin_login.html')

    else:
        return render(request, 'ad_min/admin_login.html')


def adminlogout(request):
    messages.info(request, 'Admin Logout Successful')
    return redirect('/')

# admin home...............

def adminhome(request):
    return render(request, 'ad_min/admin_home.html')

# admin requirements

def requirements(request):
    if request.method == 'POST':
        material_type = request.POST.get('material_type')
        box_size = request.POST.get('box_size')
        ocean_depth_range = request.POST.get('ocean_depth_range')
        seagrass_type = request.POST.get('seagrass_type')
        
        
        p=random.randint(1000,9999)
        
        project_id=f"Project:{p}"

        hydra(material_type=material_type,
                     box_size=box_size, 
                     ocean_depth_range=ocean_depth_range,
                     seagrass_type=seagrass_type,
                     project_id=project_id).save()
        
        messages.info(request, f"{project_id} :: Requirements Uploaded successfully.")
        
        return redirect('/adminhome/')  # Redirect to chief home after successful submission
    
    return render(request, 'ad_min/requirements.html')





# #  approve & reject..........

import random
def approve(request,id):
    data=seagrass.objects.get(id=id)
    password=random.randint(1000,9999)
    print(password)
    data.password=password
    data.emp_id=f"SG:{password}"
    data.save()

    send_mail(
        '{0}:Username and Password'.format(data.department),
        'Hello {0},\n Your {1} profile has been Approved.\n Your Username is "{2}" and Password is "{3}".\n Make sure you use this Username and Password while your logging in to the portal of {1}.\n Thank You '.format(
            data.name,data.department, data.email,data.password),
        'peddireddyajay689@gmail.com',[data.email],  # the mail which is from user registration.
        fail_silently=False,
    )

    data.approve=True
    data.reject=False
    data.save()
    messages.info(request,f"{data.emp_id} : {data.department} Approval Successful,Kindly check the registered email for the login credentials.")
    return redirect("/adminhome/")



def reject(request,id):
    data = seagrass.objects.get(id=id)
    data.approve=False
    data.reject=True
    data.save()

    subject = 'Client Rejection'
    plain_message = f"Hi {data.name},\nYour registration was rejected due to some reasons.try this later!"
    send_mail(subject, plain_message,'anvi.aadiv@gmail.com',[data.email], fail_silently=False)

    # data.delete()
    messages.info(request, "Rejection Mail Sent to Client")
    return redirect("/adminhome/")


# approve & reject..........

def aquaapprove(request):
    data = seagrass.objects.filter(department='AQUAFORGE')
    return render(request, 'ad_min/aqua_approve.html',{'data': data})

def stressapprove(request):
    data = seagrass.objects.filter(department='STRESSEVAL')
    return render(request, 'ad_min/stress_approve.html',{'data': data})

def bioapprove(request):
    data = seagrass.objects.filter(department='BIO-MONITOR')
    return render(request, 'ad_min/bio_approve.html',{'data': data})

def ecoapprove(request):
    data = seagrass.objects.filter(department='ECO-REPORT')
    return render(request, 'ad_min/eco_approve.html',{'data': data})


# manage reports..........

def aquamanage(request):
    data = hydra.objects.all()
    return render(request, 'ad_min/aqua_manage.html',{'data': data})

def stressmanage(request):
    data = hydra.objects.all()
    return render(request, 'ad_min/stress_manage.html',{'data': data})

def biomanage(request):
    data = hydra.objects.all()
    return render(request, 'ad_min/bio_manage.html',{'data': data})

def ecomanage(request):
    data = hydra.objects.all()
    return render(request, 'ad_min/eco_manage.html',{'data': data})



# MANAGE STATUS

def managestatus(request):
    data = hydra.objects.all()
    return render(request, "ad_min/manage_status.html", {'data': data})

# FINAL REPORT

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.contrib import messages


def final_report(request, project_id):
    data = hydra.objects.get(project_id=project_id)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    def draw_title_and_project_id(pdf_canvas):
        title_line1 = "MARINEROOT TOOL MANUFACTURING"
        title_line2 = "AND ENVIRONMENTAL IMPACT ANALYSIS FOR SEAGRASS GROWTH"

        pdf_canvas.setFont("Helvetica-Bold", 13)
        pdf_canvas.setFillColor(colors.blue)

        text_width1 = pdf_canvas.stringWidth(title_line1, "Helvetica-Bold", 13)
        x_position1 = (pdf_canvas._pagesize[0] - text_width1) / 2
        pdf_canvas.drawString(x_position1, 800, title_line1)

        text_width2 = pdf_canvas.stringWidth(title_line2, "Helvetica-Bold", 13)
        x_position2 = (pdf_canvas._pagesize[0] - text_width2) / 2
        pdf_canvas.drawString(x_position2, 780, title_line2)

        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.setFillColor(colors.black)
        project_id_label = "Project ID:"
        label_width = pdf_canvas.stringWidth(project_id_label, "Helvetica-Bold", 12)
        x_label = (pdf_canvas._pagesize[0] - label_width - 100) / 2
        pdf_canvas.drawString(x_label, 760, project_id_label)
        pdf_canvas.drawString(x_label + label_width + 5, 760, f"{data.project_id}")

    def draw_section(pdf_canvas, title, section_data, start_y):
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.setFillColor(colors.blue)
        pdf_canvas.drawString(50, start_y, title)
        start_y -= 10

        table_data = [[f"{item[0]}", f"{item[1]}"] for item in section_data]
        table = Table(table_data, colWidths=[200, 250])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        table.wrapOn(pdf_canvas, 400, 400)
        table.drawOn(pdf_canvas, 50, start_y - len(section_data) * 20)

        return start_y - len(section_data) * 20 - 60

    def pick_value(*values):
        for value in values:
            if value not in (None, ''):
                return value
        return "Pending"

    def parse_boolean(value):
        if value in (True, False):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered == 'true':
                return True
            if lowered == 'false':
                return False
        return None

    def format_boolean(*values):
        parsed_value = parse_boolean(pick_value(*values))
        if parsed_value is True:
            return "Yes"
        if parsed_value is False:
            return "No"
        return "Pending"

    draw_title_and_project_id(c)

    sections = [
        ("AQUAFORGE", [
            ["Surface Area of Box (cm2)", f"{pick_value(data.surface_area_of_box, data.decrypted_surface_area_of_box)}"],
            ["Volume of Material (cm3)", f"{pick_value(data.volume_of_material, data.decrypted_volume_of_material)}"],
            ["Weight of Material (g)", f"{pick_value(data.weight_of_material, data.decrypted_weight_of_material)}"],
            ["Weight in Kilograms (kg)", f"{pick_value(data.weight_in_kilograms, data.decrypted_weight_in_kilograms)}"],
        ]),
        ("STRESSEVAL", [
            ["Pressure Bar", f"{pick_value(data.pressure_bar, data.decrypted_pressure_bar)}"],
            ["Pressure Pass", format_boolean(data.pressure_pass, data.decrypted_pressure_pass)],
            ["Leakage Pass", format_boolean(data.leakage_pass, data.decrypted_leakage_pass)],
            ["Leakage Detected", format_boolean(data.leakage_detected)],
            ["Durability Score", f"{pick_value(data.durability_score, data.decrypted_durability_score)}"],
        ]),
        ("BIO-MONITOR", [
            ["Available Seed Space (cm2)", f"{pick_value(data.available_seed_space, data.decrypted_available_seed_space)}"],
            ["Seed Growth Time (days)", f"{pick_value(data.seed_growth_time, data.decrypted_seed_growth_time)}"],
        ]),
        ("ECO-REPORT", [
            ["Area Used (m2)", f"{pick_value(data.area_used)}"],
            ["CO2 Absorbed per Year (kg)", f"{pick_value(data.co2_absorbed)}"],
            ["Marine Animals Supported", f"{pick_value(data.animals_supported)}"],
            ["Coastal Protection Score (/10)", f"{pick_value(data.protection_score)}"],
        ]),
    ]

    y_position = 750
    for section_title, section_data in sections:
        y_position = draw_section(c, section_title, section_data, y_position)
        if y_position < 150:
            c.showPage()
            draw_title_and_project_id(c)
            y_position = 750

    c.save()

    pdf_data = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="MARINEROOT_REPORT_{data.project_id}.pdf"'
    response.write(pdf_data)

    data.f_report.save(f"MARINEROOT_REPORT_{data.project_id}.pdf", ContentFile(pdf_data))
    data.rep = False
    data.report = True
    data.save()

    messages.success(request, f"{data.project_id}, Report Generated successfully")
    return redirect('/managestatus/')

