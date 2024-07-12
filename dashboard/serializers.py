from rest_framework import serializers
from .models import * 


class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machines
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class DefectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defects
        fields = '__all__'

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'plant_name','is_active']

####### Dashboard related serailizers ########

class NMBDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = NMBDashboard
        fields = '__all__'

class MachineTemperaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineTemperatures
        fields = '__all__'

class MachineParametersGraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineParametersGraph
        fields = '__all__'

class DefectNotificationSerializer(serializers.ModelSerializer):
    rca1 = serializers.SerializerMethodField()
    rca2 = serializers.SerializerMethodField()
    rca3 = serializers.SerializerMethodField()
    rca4 = serializers.SerializerMethodField()
    rca5 = serializers.SerializerMethodField()
    rca6 = serializers.SerializerMethodField()

    class Meta:
        model = DefectNotification
        fields = ['id', 'defect', 'notification_text', 'rca1', 'rca2', 'rca3', 'rca4', 'rca5', 'rca6', 'recorded_date_time']

    def get_rca(self, obj, rca_number):
        lines = obj.notification_text.split('\n')
        for line in lines:
            if line.startswith(f'RCA{rca_number}'):
                _, value = line.split(':', 1)
                return value.strip()
        return None

    def get_rca1(self, obj):
        return self.get_rca(obj, 1)

    def get_rca2(self, obj):
        return self.get_rca(obj, 2)

    def get_rca3(self, obj):
        return self.get_rca(obj, 3)

    def get_rca4(self, obj):
        return self.get_rca(obj, 4)

    def get_rca5(self, obj):
        return self.get_rca(obj, 5)

    def get_rca6(self, obj):
        return self.get_rca(obj, 6)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        notification_text = representation['notification_text']
        
        # Remove RCA lines from notification_text
        lines = notification_text.split('\n')
        filtered_lines = [line for line in lines if not line.startswith('RCA')]
        representation['notification_text'] = '\n'.join(filtered_lines).strip()
        
        return representation

##### System status serializer ######    

class SystemStatusSerializer(serializers.ModelSerializer):
    machine_name = serializers.ReadOnlyField(source='machine.name')

    class Meta:
        model = SystemStatus
        fields = ['machine', 'machine_name', 'plant', 'system_status']