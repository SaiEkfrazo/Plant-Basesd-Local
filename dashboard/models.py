from django.db import models

class Plant(models.Model):
    class Meta:
        db_table = 'Plant'
    
    plant_name = models.CharField('Plant',max_length=100,blank=False,null=False,unique=True)
    # organization_name = models.ForeignKey(Organization,on_delete=models.CASCADE,null=False,blank=False)
    is_active = models.BooleanField('Is Active',default=True)


######### Object detection tables ###############

class Machines(models.Model):
    class Meta:
        db_table = 'Machines'
    name = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.SET_NULL,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.SET_NULL,null=True)
    def __str__(self):
        return self.name if self.name else ""
    
class Defects(models.Model):
    class Meta:
        db_table = 'Defects'
    name = models.CharField(max_length=100,blank=False,null=False)
    color_code = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.SET_NULL,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.name if self.name else ""
    
class Products(models.Model):  ##### Alerts Changed into Products ######
    class Meta:
        db_table = 'Products'
    name = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.SET_NULL,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.name if self.name else ""
    

class Department(models.Model):
    class Meta:
        db_table = 'Department'
    name = models.CharField(max_length=100,blank=False,null=False)
    # organization = models.ForeignKey(Organization,on_delete=models.CASCADE,blank=True,null=True)
    plant = models.ForeignKey(Plant,blank=True,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name if self.name else ""


class NMBDashboard(models.Model):
    class Meta:
        db_table = 'NMBDashboard'

    machines = models.ForeignKey(Machines,on_delete=models.CASCADE,null=False,blank=False)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=False,blank=False)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=False,blank=False)
    defects = models.ForeignKey(Defects,on_delete=models.CASCADE,blank=False,null=False)
    image = models.CharField(max_length=250,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,blank=False,null=False)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)


class LiquidPlant(models.Model): # liquid means comfort sachet plant
    class Meta:
        db_table = 'LiquidPlant'

    machines = models.ForeignKey(Machines,on_delete=models.CASCADE,null=False,blank=False)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=False,blank=False)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=False,blank=False)
    defects = models.ForeignKey(Defects,on_delete=models.CASCADE,blank=False,null=False)
    image = models.CharField(max_length=250,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,blank=False,null=False)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)

class ShampooPlant(models.Model):  ## shampoo plant 
    class Meta:
        db_table = 'ShampooPlant'

    machines = models.ForeignKey(Machines,on_delete=models.CASCADE,null=False,blank=False)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=False,blank=False)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=False,blank=False)
    defects = models.ForeignKey(Defects,on_delete=models.CASCADE,blank=False,null=False)
    image = models.CharField(max_length=250,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,blank=False,null=False)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)


class RootCauseAnalysis(models.Model):
    class Meta:
        db_table = 'Root Cause Analysis'
    
    defect = models.ForeignKey(Defects,on_delete=models.CASCADE,null=True,blank=True)
    rca1 = models.CharField(max_length=255,null=True,blank=True)
    rca2 = models.CharField(max_length=255,null=True,blank=True)
    rca3 = models.CharField(max_length=255,null=True,blank=True)
    rca4 = models.CharField(max_length=255,null=True,blank=True)
    rca5 = models.CharField(max_length=255,null=True,blank=True)
    rca6 = models.CharField(max_length=255,null=True,blank=True)



# Machine parameters models  

class MachineTemperatures(models.Model):
    class Meta:
        db_table = 'MachineTemperatures'
    machine=models.ForeignKey(Machines,on_delete=models.CASCADE,blank=False,null=False)
    horizontal = models.CharField(max_length=100,blank=True,null=True)
    teeth= models.BooleanField(blank=True,null=True,default=False)
    coder = models.BooleanField(default=False,blank=True,null=True)
    vertical = models.CharField(max_length=1000,blank=True,null=True)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=True,blank=True)


class MachineParameters(models.Model):
    class Meta:
        db_table = 'MachineParameters'
    parameter = models.CharField(max_length=200,blank=False,null=False)
    color_code = models.CharField(max_length=100,blank=False, null=False)

    def __str__(self):
        return self.parameter if self.parameter else None

class MachineParametersGraph(models.Model):
    class Meta:
        db_table = 'MachineParametersGraph'
    machine_parameter = models.ForeignKey(MachineParameters,on_delete=models.SET_NULL,blank=True,null=True)
    params_count = models.CharField(max_length=200,blank=True,null=True)
    recorded_date_time = models.CharField(max_length=200,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=True,blank=True)


class DefectNotification(models.Model):
    class Meta:
        db_table = 'DefectNotification'
    defect = models.ForeignKey(Defects,on_delete=models.CASCADE,null=False,blank=False)
    notification_text = models.TextField(null=True,blank=True)    
    recorded_date_time = models.CharField(max_length=100,blank=True,null=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=False,blank=False)

#### system status model ####

class SystemStatus(models.Model):
    class Meta:
        db_table = 'SystemStatus'
    
    machine = models.ForeignKey(Machines,on_delete=models.CASCADE,null=False,blank=False)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,null=False,blank=False)
    system_status = models.BooleanField('System Status',default=True)



    