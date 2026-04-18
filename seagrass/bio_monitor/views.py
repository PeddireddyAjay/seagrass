from django.shortcuts import render,redirect
from django.contrib import messages
from ad_min.models import seagrass,hydra
# from django.core.mail import send_mail

# # Create your views here.

# HOME

def bio_home(request):
    return render(request,"bio_monitor/bio_home.html")

# bio_monitor register and login:


def bio_register(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        print(f"Name: {name}, Email: {email}, Phone: {phone}, Department: {department}")
        seagrass(name=name,email=email,phone=phone,department=department).save()
        messages.success(request, f'Bio_monitor Registration Successful, Kindly get the approval from admin for login credentials.')
        return redirect('/')
    return render(request,'bio_monitor/reg_log.html')



def bio_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            # Try to retrieve the user with the given email and password
            user = seagrass.objects.get(email=email, password=password)

            if user:
                # Set the login field to True (1) upon successful login
                user.login = True
                user.save()

                hydra_data = hydra.objects.filter().first()  # Use first() to avoid MultipleObjectsReturned

                if hydra_data:  # Check if hydra_data exists
                    project_id = hydra_data.project_id
                    messages.info(request, f"{project_id} :: bio_monitor Login Successful")
                    return redirect("/bio_home/")
                else:
                    messages.info(request, "No hydra data found.") 
                    return redirect("/bio_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return render(request, 'bio_monitor/reg_log.html')
        except seagrass.DoesNotExist:
            # Handle case where the user with the provided credentials does not exist
            messages.info(request, "Wrong Credentials")
            return render(request, 'bio_monitor/reg_log.html')

    return render(request, 'bio_monitor/reg_log.html')





import json
import datetime
import hashlib
from django.shortcuts import render, redirect
import base64
from django.core.mail import send_mail
from django.contrib import messages
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Cybernetics class definition
class Cybernetics:
    def __init__(self):
        self.logs = []

    def log_operation(self, label, encrypted_value):
        self.logs.append({
            'timestamp': str(datetime.datetime.now()),
            'label': label,
            'encrypted_value': encrypted_value
        })

    def get_feedback(self):
        return f"Total encrypted fields processed: {len(self.logs)}"


def _get_bio_monitor_recipient_emails():
    return list(
        seagrass.objects.filter(
            department='BIO-MONITOR',
            approve=True,
        )
        .exclude(email__isnull=True)
        .exclude(email__exact='')
        .values_list('email', flat=True)
        .distinct()
    )


# Encrypt data using Twofish
def encrypt_data(plain_text, key):
    cipher = AES.new(key, AES.MODE_ECB)
    padded_text = pad(plain_text.encode('utf-8'), 16)
    encrypted_text = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted_text).decode('utf-8')


# Admin protocols using Cybernetics
def stress_final_report(request):
    data = hydra.objects.all()
    cyber = Cybernetics()

    if data.exists():
        if data[0].bio_decryption_key:
            key = base64.b64decode(data[0].bio_decryption_key)
        else:
            key = get_random_bytes(16)
    else:
        key = get_random_bytes(16)

    for item in data:
        e_pressure_bar = encrypt_data(str(item.pressure_bar) if item.pressure_bar is not None else '0', key)
        e_pressure_pass = encrypt_data(str(item.pressure_pass) if item.pressure_pass is not None else 'False', key)
        e_leakage_pass = encrypt_data(str(item.leakage_pass) if item.leakage_pass is not None else 'False', key)
        e_durability_score = encrypt_data(str(item.durability_score) if item.durability_score else '0', key)

        cyber.log_operation('pressure_bar', e_pressure_bar)
        cyber.log_operation('pressure_pass', e_pressure_pass)
        cyber.log_operation('leakage_pass', e_leakage_pass)
        cyber.log_operation('durability_score', e_durability_score)

        item.encrypted_pressure_bar = e_pressure_bar
        item.encrypted_pressure_pass = e_pressure_pass
        item.encrypted_leakage_pass = e_leakage_pass
        item.encrypted_durability_score = e_durability_score
        item.bio_decryption_key = base64.b64encode(key).decode('utf-8')
        item.save()


    return render(request, 'bio_monitor/stress_final_report.html', {'data': data})


# Generate and send decryption key
def getkey_bio(request, project_id):
    data = hydra.objects.get(project_id=project_id)

    if data.bio_decryption_key:
        encoded_key = data.bio_decryption_key
    else:
        key = get_random_bytes(16)
        encoded_key = base64.b64encode(key).decode('utf-8')
        data.bio_decryption_key = encoded_key

    data.bio_get_key = True
    data.save()

    print(f"Generated Key: {encoded_key}")

    recipient_emails = _get_bio_monitor_recipient_emails()
    if recipient_emails:
        send_mail(
            'bio_monitor: Decryption key',
            f'Hi bio_monitor,\nYour Decryption key for Decrypting "{data.project_id}" Record is "{encoded_key}".\n'
            'Please use the provided key to decrypt the records.\n\nThank You',
            'demosample47@gmail.com',
            recipient_emails,
            fail_silently=False,
        )
        messages.info(request, f"Decryption Key sent to {', '.join(recipient_emails)} Successfully.")
    else:
        messages.error(request, 'No approved BIO-MONITOR email address was found to send the key.')

    return redirect('/stress_final_report/')


# Decrypt data using Twofish
def decrypt_data(encrypted_data, key):
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_padded = cipher.decrypt(encrypted_data_bytes)
    try:
        return unpad(decrypted_padded, 16).decode('utf-8').strip()
    except ValueError:
        raise ValueError("Decrypted data is not valid or padding is incorrect")


# View for decryption form
def decrypt_data_bio(request, project_id):
    d = hydra.objects.get(project_id=project_id)
    if request.method == "POST":
        decryption_key = request.POST['decryption_key']
        key = base64.b64decode(decryption_key)

        print(f"Decryption key entered: {decryption_key}")
        print(f"Stored decryption key: {d.bio_decryption_key}")

        stored_key = base64.b64decode(d.bio_decryption_key)

        if stored_key == key:
            try:
                print(f"Encrypted hydra Length: {d.encrypted_surface_area_of_box}")

                decrypted_pressure_bar = decrypt_data(d.encrypted_pressure_bar, stored_key)
                decrypted_pressure_pass = decrypt_data(d.encrypted_pressure_pass, stored_key)
                decrypted_leakage_pass = decrypt_data(d.encrypted_leakage_pass, stored_key)
                decrypted_durability_score = decrypt_data(d.encrypted_durability_score, stored_key)

                d.decrypted_pressure_bar = decrypted_pressure_bar
                d.decrypted_pressure_pass = decrypted_pressure_pass
                d.decrypted_leakage_pass = decrypted_leakage_pass
                d.decrypted_durability_score = decrypted_durability_score

                d.bio_decrypt = True
                d.save()

                messages.info(request, f'{d.project_id}: Decryption Successful ')
                return redirect('/stress_final_report/')
            except ValueError as e:
                messages.error(request, f'Decryption error: {str(e)}')
                print(f"Decryption error: {str(e)}")
        else:
            messages.error(request, f'{d.project_id}: Wrong Key, Kindly enter the correct key to continue.')

    return redirect('/stress_final_report/')




# bio_scanning

def bio_scan(request):
    data = hydra.objects.all()
    return render(request,"bio_monitor/bio_scan.html",{'data': data})


def bio_calculation(request, project_id):
    hydra_object = hydra.objects.get(project_id=project_id)

    # 1. Set dimensions based on box_size
    box_size = hydra_object.box_size  # make sure box_size is stored in the model
    if box_size == "Small":
        length, width, height = 50, 50, 30
    elif box_size == "Medium":
        length, width, height = 80, 80, 40
    elif box_size == "Large":
        length, width, height = 100, 100, 50
    elif box_size == "Extra Large":
        length, width, height = 150, 100, 60
    else:
        length, width, height = 0, 0, 0  # fallback

    # 2. Calculate base area and usable area
    base_area = length * width
    usable_area = base_area * 0.8
    number_of_seeds = int(usable_area // 100)  # integer division for seed count

    # 3. Determine growth time based on seagrass type
    seagrass_type = hydra_object.seagrass_type
    growth_time = 0
    if seagrass_type == "Zostera marina":
        growth_time = 25
    elif seagrass_type == "Halophila ovalis":
        growth_time = 20
    elif seagrass_type == "Cymodocea serrulata":
        growth_time = 30
    elif seagrass_type == "Thalassia hemprichii":
        growth_time = 28

    # 4. Save results
    hydra_object.available_seed_space = number_of_seeds
    hydra_object.seed_growth_time = growth_time
    hydra_object.bio_scanned = True
    hydra_object.status = "bio_monitor Done"
    hydra_object.save()

    messages.info(request, f"{project_id} :: bio_monitor Processed Successfully")
    return redirect("/bio_scan/")




# bio file

def bio_file(request):
    data=hydra.objects.filter(bio_scanned=True)
    return render(request,"bio_monitor/bio_file.html",{'data':data})

# Logout

def bio_logout(request):
    messages.info(request, 'bio_monitor Logout successful')
    return redirect('/')
