from django.shortcuts import render,redirect
from django.contrib import messages
from ad_min.models import seagrass,hydra
from django.core.mail import send_mail

# Create your views here.

#HOME

def aqua_home(request):
    return render(request,"aquaforge/aqua_home.html")

# aquaforge register and login:


def aqua_register(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        print(f"Name: {name}, Email: {email}, Phone: {phone}, Department: {department}")
        seagrass(name=name,email=email,phone=phone,department=department).save()
        messages.success(request, f'Aquaforge Registration Successful, Kindly get the approval from admin for login credentials.')
        return redirect('/')
    return render(request,'aquaforge/reg_log.html')



def aqua_login(request):
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
                    messages.info(request, f"{project_id} :: aquaforge Login Successful")
                    return redirect("/aqua_home/")
                else:
                    messages.info(request, "No hydra data found.") 
                    return redirect("/aqua_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return render(request, 'aquaforge/reg_log.html')
        except seagrass.DoesNotExist:
            # Handle case where the user with the provided credentials does not exist
            messages.info(request, "Wrong Credentials")
            return render(request, 'aquaforge/reg_log.html')

    return render(request, 'aquaforge/reg_log.html')





import json
import datetime
import hashlib
from django.shortcuts import render, redirect
import base64
from django.core.mail import send_mail
from django.contrib import messages
import twofish
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


def _get_aquaforge_recipient_emails():
    return list(
        seagrass.objects.filter(
            department='AQUAFORGE',
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
def ad_min_protocols(request):
    data = hydra.objects.all()
    cyber = Cybernetics()

    if data.exists():
        if data[0].aqua_decryption_key:
            key = base64.b64decode(data[0].aqua_decryption_key)
        else:
            key = get_random_bytes(16)
    else:
        key = get_random_bytes(16)

    for item in data:
        e_material_type = encrypt_data(str(item.material_type) if item.material_type else '0', key)
        e_box_size = encrypt_data(str(item.box_size) if item.box_size else '0', key)
        e_ocean_depth_range = encrypt_data(str(item.ocean_depth_range) if item.ocean_depth_range else '0', key)
        e_seagrass_type = encrypt_data(str(item.seagrass_type) if item.seagrass_type else '0', key)

        # Cybernetics log (replaces blockchain block)
        cyber.log_operation('material_type', e_material_type)
        cyber.log_operation('box_size', e_box_size)
        cyber.log_operation('ocean_depth_range', e_ocean_depth_range)
        cyber.log_operation('seagrass_type', e_seagrass_type)

        # Save encrypted values and key
        item.encrypted_material_type = e_material_type
        item.encrypted_box_size = e_box_size
        item.encrypted_ocean_depth_range = e_ocean_depth_range
        item.encrypted_seagrass_type = e_seagrass_type
        item.aqua_decryption_key = base64.b64encode(key).decode('utf-8')
        item.save()

    return render(request, 'aquaforge/ad_min_protocols.html', {'data': data})
    

# Generate and send decryption key
def getkey_aqua(request, project_id):
    data = hydra.objects.get(project_id=project_id)

    if data.aqua_decryption_key:
        encoded_key = data.aqua_decryption_key
    else:
        key = get_random_bytes(16)
        encoded_key = base64.b64encode(key).decode('utf-8')
        data.aqua_decryption_key = encoded_key

    data.aqua_get_key = True
    data.save()

    print(f"Generated Key: {encoded_key}")

    recipient_emails = _get_aquaforge_recipient_emails()
    if recipient_emails:
        send_mail(
            'aquaforge: Decryption key',
            f'Hi aquaforge,\nYour Decryption key for Decrypting "{data.project_id}" Record is "{encoded_key}".\n'
            'Please use the provided key to decrypt the records.\n\nThank You',
            'demosample47@gmail.com',
            recipient_emails,
            fail_silently=False,
        )
        messages.info(request, f"Decryption Key sent to {', '.join(recipient_emails)} Successfully.")
    else:
        messages.error(request, 'No approved AQUAFORGE email address was found to send the key.')

    return redirect('/ad_min_protocols/')


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
def decrypt_data_aqua(request, project_id):
    d = hydra.objects.get(project_id=project_id)
    if request.method == "POST":
        decryption_key = request.POST['decryption_key']
        key = base64.b64decode(decryption_key)

        print(f"Decryption key entered: {decryption_key}")
        print(f"Stored decryption key: {d.aqua_decryption_key}")

        stored_key = base64.b64decode(d.aqua_decryption_key)

        if stored_key == key:
            try:
                print(f"Encrypted hydra Length: {d.encrypted_material_type}")
                
                decrypted_material_type = decrypt_data(d.encrypted_material_type, stored_key)
                decrypted_box_size = decrypt_data(d.encrypted_box_size, stored_key)
                decrypted_ocean_depth_range = decrypt_data(d.encrypted_ocean_depth_range, stored_key)
                decrypted_seagrass_type = decrypt_data(d.encrypted_seagrass_type, stored_key)

                d.decrypted_material_type = decrypted_material_type
                d.decrypted_box_size = decrypted_box_size
                d.decrypted_ocean_depth_range = decrypted_ocean_depth_range
                d.decrypted_seagrass_type = decrypted_seagrass_type

                d.aqua_decrypt = True
                d.save()

                messages.info(request, f'{d.project_id}: Decryption Successful ')
                return redirect('/ad_min_protocols/')
            except ValueError as e:
                messages.error(request, f'Decryption error: {str(e)}')
                print(f"Decryption error: {str(e)}")
        else:
            messages.error(request, f'{d.project_id}: Wrong Key, Kindly enter the correct key to continue.')

    return redirect('/ad_min_protocols/')





# aqua_scanning

def aqua_scan(request):
    data = hydra.objects.all()
    return render(request,"aquaforge/aqua_scan.html",{'data': data})


def aqua_calculation(request, project_id):
    hydra_object = hydra.objects.get(project_id=project_id)

    # Get user inputs
    material_type = hydra_object.material_type
    box_size = hydra_object.box_size

    # Set dimensions based on box_size
    if box_size == "Small":
        length, width, height = 50, 50, 30
    elif box_size == "Medium":
        length, width, height = 80, 80, 40
    elif box_size == "Large":
        length, width, height = 100, 100, 50
    elif box_size == "Extra Large":
        length, width, height = 150, 100, 60
    else:
        length, width, height = 0, 0, 0  # default fallback

    # Set thickness and density based on material type
    if material_type == "Plastic":
        thickness = 0.5
        density = 1.2
    elif material_type == "Fiber-reinforced plastic":
        thickness = 0.7
        density = 1.5
    elif material_type == "Recycled polymer":
        thickness = 0.6
        density = 1.3
    elif material_type == "Transparent acrylic":
        thickness = 0.4
        density = 1.1
    elif material_type == "Biodegradable plastic":
        thickness = 0.5
        density = 1.0
    else:
        thickness = 0.5
        density = 1.2  # default values

    # Surface Area (cm²)
    surface_area = 2 * (length * width + width * height + length * height)

    # Volume of Material (cm³)
    volume = surface_area * thickness

    # Weight in grams and kg
    weight_grams = volume * density
    weight_kg = weight_grams / 1000

    # Save calculated values to model fields (as string)
    hydra_object.surface_area_of_box = str(round(surface_area, 2))
    hydra_object.volume_of_material = str(round(volume, 2))
    hydra_object.weight_of_material = str(round(weight_grams, 2))
    hydra_object.weight_in_kilograms = str(round(weight_kg, 2))

    hydra_object.aqua_scanned = True
    hydra_object.status = "aquaforge Done"
    hydra_object.save()

    messages.info(request, f"{project_id} :: aquaforge Processed Successfully")
    return redirect("/aqua_scan/")




# aqua file

def aqua_file(request):
    data=hydra.objects.filter(aqua_scanned=True)
    return render(request,"aquaforge/aqua_file.html",{'data':data})

# Logout

def aqua_logout(request):
    messages.info(request, 'aquaforge Logout successful')
    return redirect('/')
