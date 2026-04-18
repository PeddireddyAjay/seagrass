# Create your models here.
from django.db import models

 

class seagrass(models.Model):

    # all modules register and login

    name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    department= models.CharField(max_length=100, null=True)


    #user_id and mail password generation

    emp_id= models.CharField(max_length=100, null=True)
    password=models.PositiveBigIntegerField(null=True)



    # admin approve and reject

    approve = models.BooleanField(default=False)
    reject = models.BooleanField(default=False)

    # login and logout

    login = models.BooleanField(default=False)
    logout = models.BooleanField(default=False)




class hydra(models.Model):

    # project_id........................................................

    project_id = models.CharField(max_length=100, null=True)

    # admin requirements and datas before ecryption.......................

    material_type = models.CharField(max_length=100, null=True)
    box_size = models.CharField(max_length=100, null=True)
    ocean_depth_range = models.CharField(max_length=100, null=True)
    seagrass_type = models.CharField(max_length=100, null=True)
    

    # Module 1 - aquaforge

    # admin requirements and datas after ecryption

    encrypted_material_type = models.CharField(max_length=100, null=True)
    encrypted_box_size = models.CharField(max_length=100, null=True)
    encrypted_ocean_depth_range = models.CharField(max_length=100, null=True)
    encrypted_seagrass_type = models.CharField(max_length=100, null=True)


    # encryption key

    aqua_decryption_key = models.CharField(max_length=64,null=True)

    # # get key and decrypt  

    aqua_get_key = models.BooleanField(default=False,null=True)
    aqua_decrypt = models.BooleanField(default=False,null=True)

    # admin requirements and datas after decryption

    decrypted_material_type = models.CharField(max_length=100, null=True)
    decrypted_box_size = models.CharField(max_length=100, null=True)
    decrypted_ocean_depth_range = models.CharField(max_length=100, null=True)
    decrypted_seagrass_type = models.CharField(max_length=100, null=True)


    # aqua - Scanning

    surface_area_of_box = models.CharField(max_length=100,null=True)
    volume_of_material = models.CharField(max_length=100, null=True)
    weight_of_material = models.CharField(max_length=100,null=True)
    weight_in_kilograms = models.CharField(max_length=100, null=True)

    # Module 2 - stresseval ........................

    encrypted_surface_area_of_box = models.CharField(max_length=256, null=True)
    encrypted_volume_of_material = models.CharField(max_length=256, null=True)
    encrypted_weight_of_material = models.CharField(max_length=256, null=True)
    encrypted_weight_in_kilograms = models.CharField(max_length=256, null=True)
    

    # encryption key

    stress_decryption_key = models.CharField(max_length=64, null=True)

    # get key and decrypt

    stress_get_key = models.BooleanField(default=False, null=True)
    stress_decrypt = models.BooleanField(default=False, null=True)

    # decryption 

    decrypted_surface_area_of_box = models.CharField(max_length=100, null=True)
    decrypted_volume_of_material = models.CharField(max_length=100, null=True)
    decrypted_weight_of_material = models.CharField(max_length=100, null=True)
    decrypted_weight_in_kilograms = models.CharField(max_length=100, null=True)

    # stress - Scanning

    pressure_bar = models.FloatField(null=True)
    pressure_pass = models.BooleanField(null=True)
    leakage_pass = models.BooleanField(null=True)
    leakage_detected = models.BooleanField(default=False)
    durability_score = models.CharField(max_length=100, null=True)



    # Module - 3 - bio-monitor

    encrypted_pressure_bar = models.TextField(null=True)
    encrypted_pressure_pass = models.TextField(null=True)
    encrypted_leakage_pass = models.TextField(null=True)
    encrypted_durability_score = models.TextField(null=True)


    # encryption key

    bio_decryption_key = models.CharField(max_length=64, null=True)

    # get key and decrypt

    bio_get_key = models.BooleanField(default=False, null=True)
    bio_decrypt = models.BooleanField(default=False, null=True)

    # decryption

    decrypted_pressure_bar = models.CharField(max_length=100, null=True)
    decrypted_pressure_pass = models.CharField(max_length=100, null=True)
    decrypted_leakage_pass = models.CharField(max_length=100, null=True)
    decrypted_durability_score = models.CharField(max_length=100, null=True)


    # biomonitor- Scanning

    available_seed_space = models.CharField(max_length=100, null=True)
    seed_growth_time = models.CharField(max_length=100, null=True)
    
    



    # Module - 4 - eco-report

    

    encrypted_available_seed_space = models.TextField(null=True)
    encrypted_seed_growth_time = models.TextField(null=True)


    # encryption key

    eco_decryption_key = models.CharField(max_length=64, null=True)

    # get key and decrypt

    eco_get_key = models.BooleanField(default=False, null=True)
    eco_decrypt = models.BooleanField(default=False, null=True)


    # decryption

    decrypted_available_seed_space = models.TextField(null=True)
    decrypted_seed_growth_time = models.TextField(null=True)

    # eco-report - Scanning

    area_used = models.FloatField(null=True, blank=True)
    co2_absorbed = models.FloatField(null=True, blank=True)
    animals_supported = models.IntegerField(null=True, blank=True)
    protection_score = models.FloatField(null=True, blank=True)


    # all modules scanned name

    aqua_scanned = models.BooleanField(default=False)
    stress_scanned =  models.BooleanField(default=False)
    bio_scanned = models.BooleanField(default=False)
    eco_scanned = models.BooleanField(default=False)
    
    

    # all modules status

    status = models.CharField(default="Pending", null=True , max_length=100)

    # # reports

    report = models.BooleanField(default=False)
    rep = models.BooleanField(default=False)

    f_report = models.FileField(null=True, upload_to="Final_Report/")