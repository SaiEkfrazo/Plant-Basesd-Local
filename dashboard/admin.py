from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from .models import *

admin.site.register(NMBDashboard)

@admin.register(RootCauseAnalysis)
class RootCauseAnalysisAdmin(ImportExportModelAdmin):
    list_display = ('id', 'defect', 'rca1', 'rca2', 'rca3','rca4','rca5','rca6')

@admin.register(Defects)
class DefectsAdmin(ImportExportModelAdmin):
    list_display = ('name','color_code','plant')

@admin.register(Machines)
class MachineAdmin(ImportExportModelAdmin):
    list_display = ('id','name', 'plant')  

@admin.register(Products)
class ProductsAdmin(ImportExportModelAdmin):
    list_display = ('id','name', 'plant') 

@admin.register(Department)
class DepartmentsAdmin(ImportExportModelAdmin):
    list_display = ('id','name', 'plant') 

@admin.register(Plant)
class PlantAdmin(ImportExportModelAdmin):
    list_display = ('id','plant_name', 'is_active')  

@admin.register(MachineTemperatures)
class MachineTemperaturesAdmin(ImportExportModelAdmin):
    list_display = ('machine', 'horizontal', 'teeth', 'coder', 'vertical', 'recorded_date_time', 'plant')


@admin.register(MachineParametersGraph)
class MachineParametersGraphAdmin(ImportExportModelAdmin):
    list_display = ('machine_parameter', 'params_count', 'recorded_date_time', 'plant')
    

@admin.register(MachineParameters)
class MachineParametersAdmin(ImportExportModelAdmin):
    list_display = ('parameter', 'color_code')


admin.site.register(DefectNotification)


@admin.register(SystemStatus)
class PlantAdmin(ImportExportModelAdmin):
    list_display = ('id','machine','plant', 'system_status')

@admin.register(LiquidPlant)
class LiqudPlantAdmin(ImportExportModelAdmin):
    list_display = ('id','machines','department','product','defects','image','plant','recorded_date_time')