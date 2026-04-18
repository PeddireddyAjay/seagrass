from django.shortcuts import render,redirect
from django.contrib import messages
from ad_min.models import seagrass,hydra
from django.core.mail import send_mail

# # Create your views here.

# HOME

def stress_home(request):
    return render(request,"stresseval/stress_home.html")

# stresseval register and login:


def stress_register(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        print(f"Name: {name}, Email: {email}, Phone: {phone}, Department: {department}")
        seagrass(name=name,email=email,phone=phone,department=department).save()
        messages.success(request, f'Stresseval Registration Successful, Kindly get the approval from admin for login credentials.')
        return redirect('/')
    return render(request,'stresseval/reg_log.html')



def stress_login(request):
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
                    messages.info(request, f"{project_id} :: stresseval Login Successful")
                    return redirect("/stress_home/")
                else:
                    messages.info(request, "No hydra data found.") 
                    return redirect("/stress_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return render(request, 'stresseval/reg_log.html')
        except seagrass.DoesNotExist:
            # Handle case where the user with the provided credentials does not exist
            messages.info(request, "Wrong Credentials")
            return render(request, 'stresseval/reg_log.html')

    return render(request, 'stresseval/reg_log.html')





import json
import datetime
import hashlib
from pathlib import Path
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


def _get_stresseval_recipient_emails():
    return list(
        seagrass.objects.filter(
            department='STRESSEVAL',
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
def aqua_final_report(request):
    data = hydra.objects.all()
    cyber = Cybernetics()

    if data.exists():
        if data[0].stress_decryption_key:
            key = base64.b64decode(data[0].stress_decryption_key)
        else:
            key = get_random_bytes(16)
    else:
        key = get_random_bytes(16)

    for item in data:
        e_surface_area_of_box = encrypt_data(str(item.surface_area_of_box) if item.surface_area_of_box else '0', key)
        e_volume_of_material = encrypt_data(str(item.volume_of_material) if item.volume_of_material else '0', key)
        e_weight_of_material = encrypt_data(str(item.weight_of_material) if item.weight_of_material else '0', key)
        e_weight_in_kilograms = encrypt_data(str(item.weight_in_kilograms) if item.weight_in_kilograms else '0', key)

        # Cybernetics log (replaces blockchain block)
        cyber.log_operation('surface_area_of_box', e_surface_area_of_box)
        cyber.log_operation('volume_of_material', e_volume_of_material)
        cyber.log_operation('weight_of_material', e_weight_of_material)
        cyber.log_operation('weight_in_kilograms', e_weight_in_kilograms)

        # Save encrypted values and key
        item.encrypted_surface_area_of_box = e_surface_area_of_box
        item.encrypted_volume_of_material = e_volume_of_material
        item.encrypted_weight_of_material = e_weight_of_material
        item.encrypted_weight_in_kilograms = e_weight_in_kilograms
        item.stress_decryption_key = base64.b64encode(key).decode('utf-8')
        item.save()

    return render(request, 'stresseval/aqua_final_report.html', {'data': data})


# Generate and send decryption key
def getkey_stress(request, project_id):
    data = hydra.objects.get(project_id=project_id)

    if data.stress_decryption_key:
        encoded_key = data.stress_decryption_key
    else:
        key = get_random_bytes(16)
        encoded_key = base64.b64encode(key).decode('utf-8')
        data.stress_decryption_key = encoded_key

    data.stress_get_key = True
    data.save()

    print(f"Generated Key: {encoded_key}")

    recipient_emails = _get_stresseval_recipient_emails()
    if recipient_emails:
        send_mail(
            'stresseval: Decryption key',
            f'Hi stresseval,\nYour Decryption key for Decrypting "{data.project_id}" Record is "{encoded_key}".\n'
            'Please use the provided key to decrypt the records.\n\nThank You',
            'demosample47@gmail.com',
            recipient_emails,
            fail_silently=False,
        )
        messages.info(request, f"Decryption Key sent to {', '.join(recipient_emails)} Successfully.")
    else:
        messages.error(request, 'No approved STRESSEVAL email address was found to send the key.')

    return redirect('/aqua_final_report/')


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
def decrypt_data_stress(request, project_id):
    d = hydra.objects.get(project_id=project_id)
    if request.method == "POST":
        decryption_key = request.POST['decryption_key']
        key = base64.b64decode(decryption_key)

        print(f"Decryption key entered: {decryption_key}")
        print(f"Stored decryption key: {d.stress_decryption_key}")

        stored_key = base64.b64decode(d.stress_decryption_key)

        if stored_key == key:
            try:
                print(f"Encrypted hydra Length: {d.encrypted_surface_area_of_box}")

                decrypted_surface_area_of_box = decrypt_data(d.encrypted_surface_area_of_box, stored_key)
                decrypted_volume_of_material = decrypt_data(d.encrypted_volume_of_material, stored_key)
                decrypted_weight_of_material = decrypt_data(d.encrypted_weight_of_material, stored_key)
                decrypted_weight_in_kilograms = decrypt_data(d.encrypted_weight_in_kilograms, stored_key)

                d.decrypted_surface_area_of_box = decrypted_surface_area_of_box
                d.decrypted_volume_of_material = decrypted_volume_of_material
                d.decrypted_weight_of_material = decrypted_weight_of_material
                d.decrypted_weight_in_kilograms = decrypted_weight_in_kilograms

                d.stress_decrypt = True
                d.save()

                messages.info(request, f'{d.project_id}: Decryption Successful ')
                return redirect('/aqua_final_report/')
            except ValueError as e:
                messages.error(request, f'Decryption error: {str(e)}')
                print(f"Decryption error: {str(e)}")
        else:
            messages.error(request, f'{d.project_id}: Wrong Key, Kindly enter the correct key to continue.')

    return redirect('/aqua_final_report/')





# stress_scanning

def stress_scan(request):
    data = hydra.objects.all()
    return render(request,"stresseval/stress_scan.html",{'data': data})


import joblib
import pandas as pd
import numpy as np
from django.contrib import messages
from django.shortcuts import redirect

def stress_calculation(request, project_id):
    # Import ML dependencies lazily so the web process can boot on low-memory hosts.
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import MinMaxScaler
    from pytorch_tabnet.tab_model import TabNetRegressor

    hydra_object = hydra.objects.get(project_id=project_id)

    # -----------------------------
    # Pressure Test (Corrected)
    # -----------------------------
    try:
        weight_grams = float(hydra_object.weight_of_material)
        depth_meters = weight_grams / 1000.0  # Convert grams to kg/meters (if representing depth)
    except:
        depth_meters = 0.0

    pressure_bar = round(depth_meters * 0.1, 2)
    pressure_pass = pressure_bar <= 3.0

    # -----------------------------
    # Leakage Test
    # -----------------------------
    leakage_pass = not hydra_object.leakage_detected

    # -----------------------------
    # Durability Prediction
    # -----------------------------
    dataset_path = Path(__file__).resolve().parents[1] / "durability_test.csv"
    if not dataset_path.exists():
        messages.error(request, f"Durability dataset not found: {dataset_path}")
        return redirect("/stress_scan/")

    df = pd.read_csv(dataset_path)

    # Feature extraction
    df['surface'] = df['surface_area_of_box'].astype(float)
    df['volume'] = df['volume_of_material'].astype(float)
    df['depth'] = df['weight_of_material'].astype(float)
    df['seagrass'] = df['weight_in_kilograms'].astype(float)
    df['durability'] = df['durability_score'].astype(float)

    # Features & target
    X = df[['surface', 'volume', 'depth', 'seagrass']].values
    y = df['durability'].values.reshape(-1, 1)

    # Normalize features
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

    # Model training
    reg = TabNetRegressor(verbose=0)
    reg.fit(X_train, y_train, max_epochs=200, patience=20)

    # Save model and scalers
    joblib.dump(reg, "tabnet_model.pkl")
    joblib.dump(scaler_X, "scalerX.pkl")
    joblib.dump(scaler_y, "scalerY.pkl")

    # -----------------------------
    # Prediction for current object
    # -----------------------------
    try:
        input_surface = float(hydra_object.surface_area_of_box)
        input_volume = float(hydra_object.volume_of_material)
        input_depth = float(hydra_object.weight_of_material)
        input_seagrass = float(hydra_object.weight_in_kilograms)
    except:
        input_surface = input_volume = input_depth = input_seagrass = 0.0

    input_data = np.array([[input_surface, input_volume, input_depth, input_seagrass]])
    input_scaled = scaler_X.transform(input_data)
    durability_pred_scaled = reg.predict(input_scaled)
    durability_score = float(scaler_y.inverse_transform(durability_pred_scaled)[0][0])
    durability_score = round(min(max(durability_score, 0), 100), 2)  # Clamp between 0 and 100

    # -----------------------------
    # Save results
    # -----------------------------
    hydra_object.pressure_bar = pressure_bar
    hydra_object.pressure_pass = pressure_pass
    hydra_object.leakage_pass = leakage_pass
    hydra_object.durability_score = durability_score
    hydra_object.stress_scanned = True
    hydra_object.status = "stresseval Done"
    hydra_object.save()

    messages.info(request, f"{project_id} :: Pressure, Leakage & Durability Done")
    return redirect("/stress_scan/")





# stress file

def stress_file(request):
    data=hydra.objects.filter(stress_scanned=True)
    return render(request,"stresseval/stress_file.html",{'data':data})

# Logout

def stress_logout(request):
    messages.info(request, 'stresseval Logout successful')
    return redirect('/')
