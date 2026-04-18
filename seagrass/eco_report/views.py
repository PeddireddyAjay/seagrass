from django.shortcuts import render, redirect
from django.contrib import messages
from ad_min.models import seagrass, hydra
from django.core.mail import send_mail
import json
import datetime
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# HOME

def eco_home(request):
    return render(request, "eco_report/eco_home.html")

# ECO_REPORT REGISTER AND LOGIN

def eco_register(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        print(f"Name: {name}, Email: {email}, Phone: {phone}, Department: {department}")
        seagrass(name=name, email=email, phone=phone, department=department).save()
        messages.success(request, f'eco_report Registration Successful, Kindly get the approval from admin for login credentials.')
        return redirect('/')
    return render(request, 'eco_report/reg_log.html')


def eco_login(request):
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
                    messages.info(request, f"{project_id} :: eco_report Login Successful")
                    return redirect("/eco_home/")
                else:
                    messages.info(request, "No hydra data found.") 
                    return redirect("/eco_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return render(request, 'eco_report/reg_log.html')
        except seagrass.DoesNotExist:
            # Handle case where the user with the provided credentials does not exist
            messages.info(request, "Wrong Credentials")
            return render(request, 'eco_report/reg_log.html')

    return render(request, 'eco_report/reg_log.html')


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


def _get_eco_report_recipient_emails():
    return list(
        seagrass.objects.filter(
            department='ECO-REPORT',
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
def bio_final_report(request):
    data = hydra.objects.all()
    cyber = Cybernetics()

    if data.exists():
        if data[0].eco_decryption_key:
            key = base64.b64decode(data[0].eco_decryption_key)
        else:
            key = get_random_bytes(16)
    else:
        key = get_random_bytes(16)

    for item in data:
        e_seed_space = encrypt_data(str(item.available_seed_space) if item.available_seed_space else '0', key)
        e_growth_time = encrypt_data(str(item.seed_growth_time) if item.seed_growth_time else '0', key)

        cyber.log_operation('available_seed_space', e_seed_space)
        cyber.log_operation('seed_growth_time', e_growth_time)

        item.encrypted_available_seed_space = e_seed_space
        item.encrypted_seed_growth_time = e_growth_time
        item.eco_decryption_key = base64.b64encode(key).decode('utf-8')
        item.save()

    return render(request, 'eco_report/bio_final_report.html', {'data': data})


# Generate and send decryption key
def getkey_eco(request, project_id):
    data = hydra.objects.get(project_id=project_id)

    if data.eco_decryption_key:
        encoded_key = data.eco_decryption_key
    else:
        key = get_random_bytes(16)
        encoded_key = base64.b64encode(key).decode('utf-8')
        data.eco_decryption_key = encoded_key

    data.eco_get_key = True
    data.save()

    print(f"Generated Key: {encoded_key}")

    recipient_emails = _get_eco_report_recipient_emails()
    if recipient_emails:
        send_mail(
            'eco-report: Decryption key',
            f'Hi eco-report,\nYour Decryption key for Decrypting "{data.project_id}" Record is "{encoded_key}".\n'
            'Please use the provided key to decrypt the records.\n\nThank You',
            'demosample47@gmail.com',
            recipient_emails,
            fail_silently=False,
        )
        messages.info(request, f"Decryption Key sent to {', '.join(recipient_emails)} Successfully.")
    else:
        messages.error(request, 'No approved ECO-REPORT email address was found to send the key.')

    return redirect('/bio_final_report/')


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
def decrypt_data_eco(request, project_id):
    d = hydra.objects.get(project_id=project_id)
    if request.method == "POST":
        decryption_key = request.POST['decryption_key']
        key = base64.b64decode(decryption_key)

        print(f"Decryption key entered: {decryption_key}")
        print(f"Stored decryption key: {d.eco_decryption_key}")

        stored_key = base64.b64decode(d.eco_decryption_key)

        if stored_key == key:
            try:
                decrypted_seed_space = decrypt_data(d.encrypted_available_seed_space, stored_key)
                decrypted_growth_time = decrypt_data(d.encrypted_seed_growth_time, stored_key)

                d.decrypted_available_seed_space = decrypted_seed_space
                d.decrypted_seed_growth_time = decrypted_growth_time

                d.eco_decrypt = True
                d.save()

                messages.info(request, f'{d.project_id}: Decryption Successful ')
                return redirect('/bio_final_report/')
            except ValueError as e:
                messages.error(request, f'Decryption error: {str(e)}')
                print(f"Decryption error: {str(e)}")
        else:
            messages.error(request, f'{d.project_id}: Wrong Key, Kindly enter the correct key to continue.')

    return redirect('/bio_final_report/')





# eco_scanning

def eco_scan(request):
    data = hydra.objects.all()
    return render(request,"eco_report/eco_scan.html",{'data': data})


def eco_calculation(request, project_id):
    hydra_object = hydra.objects.get(project_id=project_id)

    # Step 1: Area Calculation
    box_length = 80  # in cm
    box_width = 80   # in cm
    base_area_cm2 = box_length * box_width                   # 6400 cm²
    usable_area_cm2 = base_area_cm2 * 0.8                    # 5120 cm²
    usable_area_m2 = usable_area_cm2 / 10000                 # convert to m² → 0.512 m²

    # Step 2: CO2 absorbed (kg/year)
    co2_per_m2 = 83.6
    co2_absorbed = round(usable_area_m2 * co2_per_m2, 2)     # 42.79 kg

    # Step 3: Marine animals supported
    animals_per_m2 = 30
    animals_supported = int(usable_area_m2 * animals_per_m2) # ≈ 15

    # Step 4: Coastal Protection Score (fixed value)
    protection_score = 9.5

    # Assign values to model fields (make sure these fields exist in your model)
    hydra_object.area_used = usable_area_m2
    hydra_object.co2_absorbed = co2_absorbed
    hydra_object.animals_supported = animals_supported
    hydra_object.protection_score = protection_score

    # Status update
    hydra_object.eco_scanned = True
    hydra_object.status = "eco_report Done"
    hydra_object.rep = True
    hydra_object.save()

    messages.info(request, f"{project_id} :: eco_report Processed Successfully")
    return redirect("/eco_scan/")



# eco file

def eco_file(request):
    data=hydra.objects.filter(eco_scanned=True)
    return render(request,"eco_report/eco_file.html",{'data':data})

# Logout

def eco_logout(request):
    messages.info(request, 'eco_report Logout successful')
    return redirect('/')
