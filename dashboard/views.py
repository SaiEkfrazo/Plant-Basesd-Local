from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import base64
import uuid
from django.core.files.base import ContentFile
import base64
import uuid
from django.conf import settings
from django.db.models import Max
from django.db.models.functions import Cast
from django.db.models import DateField
import os
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import connection
from datetime import datetime
from utils.digital_space import *
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import F
from django.db.models.functions import TruncDate
from django.db.models import Sum, Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import re
from django.core.files.storage import default_storage
from django.conf import settings
import os
from utils.custom_pagination import *
from django.db.models import Count
from datetime import timedelta, date
# Create your views here.


# import os
# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
# import base64
# import uuid
# import re

class MachineAPIView(viewsets.ModelViewSet):
    queryset = Machines.objects.all()
    serializer_class = MachineSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=MachineSerializer,
        operation_summary="Create a Machine",
        responses={
            201: openapi.Response(description="Machine created successfully"),
            400: openapi.Response(description="Machine with this name already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Machines.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'Machine with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'Machine created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=MachineSerializer,
        operation_summary="Update a Machine",
        responses={
            200: openapi.Response(description="Machine updated successfully"),
            400: openapi.Response(description="Machine with this name already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Machines.objects.exclude(id=instance.id).filter(plant=plant, name=name).exists():
            return Response({'message': 'Machine with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'Machine updated successfully'}, status=status.HTTP_200_OK)

    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter machines by plnat name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search machines by name'
            )
        ],
        operation_summary="List Machines",
        responses={200: MachineSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})
    
    @swagger_auto_schema(
        operation_summary="Delete a Machine",
        responses={
            204: openapi.Response(description="Machine deleted successfully"),
            404: openapi.Response(description="Machine not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Machine deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class ProductAPIView(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ProductSerializers,
        operation_summary="Create an Alert",
        responses={
            201: openapi.Response(description="Alert created successfully"),
            400: openapi.Response(description="Alert with this name already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Products.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'Alert with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'Alert created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=ProductSerializers,
        operation_summary="Update an Alert",
        responses={
            200: openapi.Response(description="Alert updated successfully"),
            400: openapi.Response(description="Alert with this name already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Products.objects.exclude(id=instance.id).filter(plant=plant, name=name).exists():
            return Response({'message': 'Alert with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'Alert updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter Products by plant name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search Products by name'
            )
        ],
        operation_summary="List Products",
        responses={200: ProductSerializers(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})

    @swagger_auto_schema(
        operation_summary="Delete an Alert",
        responses={
            204: openapi.Response(description="Alert deleted successfully"),
            404: openapi.Response(description="Alert not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Alert deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class DepartmentAPIView(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=DepartmentSerializer,
        operation_summary="Create a Department",
        responses={
            201: openapi.Response(description="Department created successfully"),
            400: openapi.Response(description="Department with this name already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Department.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'Department with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'Department created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=DepartmentSerializer,
        operation_summary="Update a Department",
        responses={
            200: openapi.Response(description="Department updated successfully"),
            400: openapi.Response(description="Department with this name already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')

        if Department.objects.exclude(id=instance.id).filter(plant=plant, name=name).exists():
            return Response({'message': 'Department with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'Department updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter departments by plant name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search departments by name'
            )
        ],
        operation_summary="List Departments",
        responses={200: DepartmentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})

    @swagger_auto_schema(
        operation_summary="Delete a Department",
        responses={
            204: openapi.Response(description="Department deleted successfully"),
            404: openapi.Response(description="Department not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Department deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class DefectAPIView(viewsets.ModelViewSet):
    queryset = Defects.objects.all()
    serializer_class = DefectsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=DefectsSerializer,
        operation_summary="Create a Defect",
        responses={
            201: openapi.Response(description="Defect created successfully"),
            400: openapi.Response(description="Defect with this name and color code already exists in this plant")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name').strip()
        color_code = serializer.validated_data.get('color_code').strip()

        if Defects.objects.filter(plant=plant, name=name).exists():
            return Response({'message': 'Defect with this name already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        if Defects.objects.filter(plant=plant, color_code=color_code).exists():
            return Response({'message': 'Defect with this color code already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response({'message': 'Defect created successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=DefectsSerializer,
        operation_summary="Update a Defect",
        responses={
            200: openapi.Response(description="Defect updated successfully"),
            400: openapi.Response(description="Defect with this name and color code already exists in this plant")
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        plant = serializer.validated_data.get('plant')
        name = serializer.validated_data.get('name')
        color_code = serializer.validated_data.get('color_code')

        if Defects.objects.exclude(id=instance.id).filter(plant=plant, name=name, color_code=color_code).exists():
            return Response({'message': 'Defect with this name and color code already exists in this plant'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response({'message': 'Defect updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='plant_name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter defects by Plant name'
            ),
            openapi.Parameter(
                name='key',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search defects by name'
            )
        ],
        operation_summary="List Defects",
        responses={200: DefectsSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        plant_name = request.query_params.get('plant_name')
        search = request.query_params.get('key')
        queryset = self.get_queryset()

        if plant_name:
            plant_name = plant_name.strip()
            queryset = queryset.filter(plant__plant_name__icontains=plant_name)

        if search:
            search = search.strip()
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Machines list retrieved successfully', 'results': serializer.data})
    
    @swagger_auto_schema(
        operation_summary="Delete a Defect",
        responses={
            204: openapi.Response(description="Defect deleted successfully"),
            404: openapi.Response(description="Defect not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Defect deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
####### Plant API View #######

class PlantAPIView(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        # manual_parameters=[
        # openapi.Parameter(
        #     name='organization_id',
        #     in_=openapi.IN_QUERY,
        #     type=openapi.TYPE_STRING,
        #     description='Give the Organization id to see all the plants in the organization'
        # )
        # ],
        operation_summary="List all Plants",
        responses={200: PlantSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        # organization_id = request.query_params.get('organization_id')
        # if not request.user.is_superuser:
        #     return Response({'message':'You are not allowed to view these.'}, status=status.HTTP_403_FORBIDDEN)
        # if organization_id:
        #     queryset = self.get_queryset().filter(organization_name_id=organization_id)
        # else:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': 'Plants list retrieved successfully', 'results': serializer.data})
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            
            properties={
                'plant_name': openapi.Schema(type=openapi.TYPE_STRING),
                # 'organization_name': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            required=['is_active','plant_name']
        ),
        operation_summary="Create a Plant",

    )
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'message': 'Only superuser is permitted to create plant'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if a plant with the same name already exists
        plant_name = request.data.get('plant_name')
        if Plant.objects.filter(plant_name=plant_name).exists():
            return Response({'message': 'A plant with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': "Plant Created Successfully"}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary="Delete a Plant",
        operation_description="Delete a Plant based on its ID.",
        responses={204: "Plant deleted successfully"}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_superuser:
            return Response({'error': 'Only superuser is permitted to delete plant'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({'message': "Plant Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'plant_name': openapi.Schema(type=openapi.TYPE_STRING),
            # 'organization_name': openapi.Schema(type=openapi.TYPE_INTEGER),
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
        },
        required=['is_active', 'plant_name']
    ),
    operation_summary="Update a Plant",
    responses={
        200: openapi.Response(
            description="Plant updated successfully",
            examples={
                "application/json": {
                    "message": "Plant updated successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad Request",
            examples={
                "application/json": {
                    "error": "A plant with the name already exists."
                }
            }
        )
    }
)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if the updated plant_name already exists
        plant_name = serializer.validated_data.get('plant_name')
        existing_plant = Plant.objects.exclude(id=instance.id).filter(plant_name=plant_name).first()
        if existing_plant:
            return Response({'error': f'A plant with the name "{plant_name}" already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response({'message': 'Plant updated successfully'}, status=status.HTTP_200_OK)

import os
from django.conf import settings
from django.core.files.storage import default_storage
import base64
import uuid
import re
from rest_framework import status
from rest_framework.response import Response

@method_decorator(csrf_exempt, name='dispatch')
class DashboardAPIView(viewsets.ModelViewSet):
    queryset = NMBDashboard.objects.all()
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    MODEL_MAPPING = {
        2: NMBDashboard,
        3: LiquidPlant,
        4: ShampooPlant,
    }

    @swagger_auto_schema(
        operation_summary="Create a Record",
        operation_description="Upload an image",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'base64_image': openapi.Schema(type=openapi.TYPE_STRING, description='Base64 encoded image'),
                'machines_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Machine ID'),
                'department_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Department ID'),
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product ID'),
                'defects_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Defect ID'),
                'plant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Plant ID'),
                'recorded_date_time': openapi.Schema(type=openapi.TYPE_STRING, description='Recorded Date Time'),
                'rca': openapi.Schema(type=openapi.TYPE_STRING, description='RCA')
            },
            required=['base64_image', 'machines_id', 'department_id', 'product_id', 'defects_id', 'plant_id', 'recorded_date_time']
        ),
        responses={
            201: openapi.Response(description="Record created successfully"),
            400: openapi.Response(description="Missing required fields or failed to upload image"),
            500: openapi.Response(description="Failed to save data")
        }
    )
    def create(self, request, *args, **kwargs):
        base64_image = request.data.get('base64_image', '')
        machines_id = request.data.get('machines_id', None)
        department_id = request.data.get('department_id', None)
        product_id = request.data.get('product_id', None)
        defects_id = request.data.get('defects_id', None)
        plant_id = request.data.get('plant_id', None)
        recorded_date_time = request.data.get('recorded_date_time', None)
        rca_field = request.data.get('rca', None)  # Changed from rca_id to rca_field

        # Validate if all required fields are provided
        if not all([base64_image, machines_id, department_id, product_id, defects_id, plant_id, recorded_date_time]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a unique file name using the provided fields
        file_name = f"{plant_id}_{defects_id}_{recorded_date_time}.png"

        # Decode the base64 image and save it to the media directory
        try:
            decoded_image = base64.b64decode(base64_image)
            media_path = os.path.join(settings.MEDIA_ROOT, 'images')
            os.makedirs(media_path, exist_ok=True)  # Ensure the directory exists
            path = os.path.join(media_path, file_name)
            with default_storage.open(path, 'wb') as f:
                f.write(decoded_image)
        except Exception as e:
            return Response({'error': f'Failed to upload image: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        image_url = os.path.join(settings.MEDIA_URL, 'images', file_name)

        try:
            # Determine the model to use based on the plant_id
            model = self.MODEL_MAPPING.get(plant_id)
            if not model:
                return Response({'error': 'Invalid plant_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new record in the appropriate model
            record = model.objects.create(
                machines_id=machines_id,
                department_id=department_id,
                product_id=product_id,
                defects_id=defects_id,
                plant_id=plant_id,
                image=image_url,  # Save the local URL in the image field
                recorded_date_time=recorded_date_time
            )
            print('record',record)
            recorded_date = recorded_date_time[:10]

            machine_parameter = MachineParameters.objects.filter(parameter="Reject Counter").first()
            if machine_parameter:
                machine_params_obj, created = MachineParametersGraph.objects.get_or_create(
                    recorded_date_time=recorded_date,
                    machine_parameter=machine_parameter,
                    plant_id=plant_id
                )
                if not created:
                    machine_params_obj.params_count = F('params_count') + 1
                    machine_params_obj.save()
                else:
                    machine_params_obj.params_count = 1
                    machine_params_obj.save()

            # Check if the same defect occurred three times consecutively
            last_three_records = model.objects.filter(plant_id=plant_id).order_by('-id')[:3]

            if last_three_records.count() == 3:
                defects = [record.defects for record in last_three_records]
                if all(defect == last_three_records[0].defects for defect in defects):
                    # Get the RCA for the defect
                    rca = RootCauseAnalysis.objects.filter(defect_id=defects_id).first()
                    if rca:
                        notification_text = f"Defect '{rca.defect.name}' has occurred three times consecutively.\n"
                        if rca_field and hasattr(rca, rca_field):
                            notification_text += f"{rca_field.upper()}: {getattr(rca, rca_field)}\n"
                        else:
                            if rca.rca1:
                                notification_text += f"RCA1: {rca.rca1}\n"
                            if rca.rca2:
                                notification_text += f"RCA2: {rca.rca2}\n"
                            if rca.rca3:
                                notification_text += f"RCA3: {rca.rca3}\n"
                            if rca.rca4:
                                notification_text += f"RCA4: {rca.rca4}\n"
                            if rca.rca5:
                                notification_text += f"RCA5: {rca.rca5}\n"
                            if rca.rca6:
                                notification_text += f"RCA6: {rca.rca6}\n"
                    else:
                        notification_text = f"Defect '{last_three_records[0].defects.name}' has occurred three times consecutively."

                    DefectNotification.objects.create(
                        defect_id=defects_id,
                        notification_text=notification_text,
                        recorded_date_time=recorded_date_time,
                        plant_id=plant_id,
                    )

                    # Send the notification via WebSockets to the specific plant_id room
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{plant_id}',
                        {
                            'type': 'send_notification',
                            'notification': notification_text
                        }
                    )

            return Response({'message': 'Record created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Failed to save data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_PATH, description="Plant ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('pk', openapi.IN_PATH, description="Primary Key", type=openapi.TYPE_INTEGER),
        ],
        operation_description="Delete a record and its associated image",
        responses={
            204: openapi.Response(description="Record and image deleted successfully"),
            404: openapi.Response(description="Record not found"),
            500: openapi.Response(description="Failed to delete record")
        }
    )
    def destroy(self, request, plant_id=None, pk=None, *args, **kwargs):
        try:
            print('in if')
            model = self.MODEL_MAPPING.get(plant_id)
            if not model:
                return Response({'error': 'Invalid plant_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

            record = model.objects.get(pk=pk)
            delete_image_from_space(record.image)
            record.delete()
            return Response({'message': 'Record and image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Failed to delete record: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('from_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('to_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('machine_id', openapi.IN_QUERY, description="Machine ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('department_id', openapi.IN_QUERY, description="Department ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('product_id', openapi.IN_QUERY, description="Product ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('defect_id', openapi.IN_QUERY, description="Defect ID", type=openapi.TYPE_INTEGER),
        ],
        operation_description="List defect counts for a specific plant within the specified date range and filters",
        responses={
            200: openapi.Response(description="Records retrieved successfully"),
            400: openapi.Response(description="Missing or invalid parameters"),
            404: openapi.Response(description="Plant not found"),
            500: openapi.Response(description="Failed to retrieve records")
        },
        operation_summary="Dashboard Data"
    )
    def list(self, request, *args, **kwargs):
        plant_id = request.query_params.get('plant_id', None)
        from_date_str = request.query_params.get('from_date', None)
        to_date_str = request.query_params.get('to_date', None)
        machine_id = request.query_params.get('machine_id', None)
        department_id = request.query_params.get('department_id', None)
        product_id = request.query_params.get('product_id', None)
        defect_id = request.query_params.get('defect_id', None)
    
        if not plant_id:
            return Response({"message": "plant_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant_id = int(plant_id)
        except ValueError:
            return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        model = self.MODEL_MAPPING.get(plant_id)
        if not model:
            return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if from_date_str:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            else:
                from_date = datetime.now().date() - timedelta(days=7)

            if to_date_str:
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            else:
                to_date = datetime.now().date()

            if from_date > to_date:
                return Response({"message": "from_date cannot be after to_date."}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError:
            return Response({"message": "Invalid date format provided. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            filter_criteria = {'plant_id': plant_id}

            if machine_id:
                filter_criteria['machines__id'] = machine_id

            if department_id:
                filter_criteria['department__id'] = department_id

            if product_id:
                filter_criteria['product__id'] = product_id

            if defect_id:
                filter_criteria['defects__id'] = defect_id

            queryset = model.objects.filter(**filter_criteria)

            response_data = defaultdict(lambda: defaultdict(int))
            products_set = set()

            for record in queryset:
                if not record.recorded_date_time:
                    continue

                try:
                    datetime_obj = datetime.strptime(record.recorded_date_time, '%Y-%m-%dT%H:%M:%S')
                    date = datetime_obj.date()
                except ValueError:
                    continue

                if from_date <= date <= to_date:
                    try:
                        defect = Defects.objects.get(id=record.defects_id)
                        defect_name = defect.name
                    except Defects.DoesNotExist:
                        continue

                    product_name = record.product.name
                    products_set.add(product_name)
                    response_data[str(date)][defect_name] += 1

            products_list = list(products_set)

            response_structure = dict(response_data)
            response_structure['active_products'] = products_list

            return Response(response_structure, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Failed to retrieve records: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Now having the reports data according to the plant id 

# class ReportsAPIView(viewsets.ViewSet):
#     # authentication_classes = [JWTAuthentication]
#     # permission_classes = [IsAuthenticated]

#     MODEL_MAPPING = {
#         2: NMBDashboard,
#         3: LiquidPlant,
#         4: ShampooPlant,
#     }

#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('from_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
#             openapi.Parameter('to_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
#             openapi.Parameter('machine_id', openapi.IN_QUERY, description="Machine ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('department_id', openapi.IN_QUERY, description="Department ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('product_id', openapi.IN_QUERY, description="Product ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('defect_id', openapi.IN_QUERY, description="Defect ID", type=openapi.TYPE_INTEGER),
#         ],
#         operation_description="List defect counts for a specific plant within the specified date range and filters",
#         responses={
#             200: openapi.Response(description="Records retrieved successfully"),
#             400: openapi.Response(description="Missing or invalid parameters"),
#             404: openapi.Response(description="Plant not found"),
#             500: openapi.Response(description="Failed to retrieve records")
#         },
#         operation_summary="Reports Data"
#     )
#     def list(self, request, *args, **kwargs):
#         plant_id = request.query_params.get('plant_id', None)
#         from_date_str = request.query_params.get('from_date', None)
#         to_date_str = request.query_params.get('to_date', None)
#         machine_id = request.query_params.get('machine_id', None)
#         department_id = request.query_params.get('department_id', None)
#         product_id = request.query_params.get('product_id', None)
#         defect_id = request.query_params.get('defect_id', None)
    
#         if not plant_id:
#             return Response({"message": "plant_id is required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             plant_id = int(plant_id)
#         except ValueError:
#             return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

#         model = self.MODEL_MAPPING.get(plant_id)
#         if not model:
#             return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Prepare filter criteria
#             filter_criteria = {}

#             if machine_id:
#                 filter_criteria['machines__id'] = machine_id

#             if department_id:
#                 filter_criteria['department__id'] = department_id

#             if product_id:
#                 filter_criteria['product__id'] = product_id

#             if defect_id:
#                 filter_criteria['defects__id'] = defect_id

#             # Apply date range filters
#             queryset = model.objects.filter(**filter_criteria)

#             if from_date_str:
#                 queryset = queryset.filter(recorded_date_time__gte=f"{from_date_str}T00:00:00")

#             if to_date_str:
#                 queryset = queryset.filter(recorded_date_time__lte=f"{to_date_str}T23:59:59")

#             # Order by recorded_date_time in descending order to get latest records first
#             queryset = queryset.order_by('-recorded_date_time')

#             # Serialize queryset to return all fields
#             response_data = []
#             for record in queryset:
#                 # Fetch related names
#                 machine_name = Machines.objects.get(id=record.machines_id).name if record.machines_id else None
#                 department_name = Department.objects.get(id=record.department_id).name if record.department_id else None
#                 product_name = Products.objects.get(id=record.product_id).name if record.product_id else None
#                 defect_name = Defects.objects.get(id=record.defects_id).name if record.defects_id else None
#                 plant_name = model.__name__

#                 serialized_data = {
#                     'id': record.id,
#                     'machine': machine_name,
#                     'department': department_name,
#                     'product': product_name,
#                     'defect': defect_name,
#                     'image': record.image,
#                     'plant': plant_name,
#                     'recorded_date_time': record.recorded_date_time,
#                 }
#                 response_data.append(serialized_data)

#             return Response({'results': response_data}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"message": f"Failed to retrieve records: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class ReportsAPIView(viewsets.ViewSet):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    MODEL_MAPPING = {
        2: NMBDashboard,
        3: LiquidPlant,
        4: ShampooPlant,
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('from_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('to_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('machine_id', openapi.IN_QUERY, description="Machine ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('department_id', openapi.IN_QUERY, description="Department ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('product_id', openapi.IN_QUERY, description="Product ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('defect_id', openapi.IN_QUERY, description="Defect ID", type=openapi.TYPE_INTEGER),
        ],
        operation_description="List defect counts for a specific plant within the specified date range and filters",
        responses={
            200: openapi.Response(description="Records retrieved successfully"),
            400: openapi.Response(description="Missing or invalid parameters"),
            404: openapi.Response(description="Plant not found"),
            500: openapi.Response(description="Failed to retrieve records")
        },
        operation_summary="Reports Data"
    )
    def list(self, request, *args, **kwargs):
        plant_id = request.query_params.get('plant_id', None)
        from_date_str = request.query_params.get('from_date', None)
        to_date_str = request.query_params.get('to_date', None)
        machine_id = request.query_params.get('machine_id', None)
        department_id = request.query_params.get('department_id', None)
        product_id = request.query_params.get('product_id', None)
        defect_id = request.query_params.get('defect_id', None)
    
        if not plant_id:
            return Response({"message": "plant_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant_id = int(plant_id)
        except ValueError:
            return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        model = self.MODEL_MAPPING.get(plant_id)
        if not model:
            return Response({"message": "Invalid plant_id provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Prepare filter criteria
            filter_criteria = {}

            if machine_id:
                filter_criteria['machines__id'] = machine_id

            if department_id:
                filter_criteria['department__id'] = department_id

            if product_id:
                filter_criteria['product__id'] = product_id

            if defect_id:
                filter_criteria['defects__id'] = defect_id

            # Apply date range filters
            queryset = model.objects.filter(**filter_criteria)

            if from_date_str:
                queryset = queryset.filter(recorded_date_time__gte=f"{from_date_str}T00:00:00")

            if to_date_str:
                queryset = queryset.filter(recorded_date_time__lte=f"{to_date_str}T23:59:59")

            # Order by recorded_date_time in descending order to get latest records first
            queryset = queryset.order_by('-recorded_date_time')

            # Pagination
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            # Serialize paginated queryset to return all fields
            response_data = []
            for record in paginated_queryset:
                # Fetch related names
                machine_name = Machines.objects.get(id=record.machines_id).name if record.machines_id else None
                department_name = Department.objects.get(id=record.department_id).name if record.department_id else None
                product_name = Products.objects.get(id=record.product_id).name if record.product_id else None
                defect_name = Defects.objects.get(id=record.defects_id).name if record.defects_id else None
                plant_name = model.__name__

                serialized_data = {
                    'id': record.id,
                    'machine': machine_name,
                    'department': department_name,
                    'product': product_name,
                    'defect': defect_name,
                    'image': record.image,
                    'plant': plant_name,
                    'recorded_date_time': record.recorded_date_time,
                }
                response_data.append(serialized_data)

            return paginator.get_paginated_response(response_data)

        except Exception as e:
            return Response({"message": f"Failed to retrieve records: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AISmartAPIView(viewsets.ViewSet):
    MODEL_MAPPING = {
        2: NMBDashboard,
        3: LiquidPlant,
        4: ShampooPlant,
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('defect_id', openapi.IN_QUERY, description="Defect ID", type=openapi.TYPE_INTEGER),
        ],
        operation_description="List defect counts for a specific plant within the specified date range and filters",
        responses={
            200: openapi.Response(description="Records retrieved successfully"),
            400: openapi.Response(description="Missing or invalid parameters"),
            404: openapi.Response(description="Plant not found"),
            500: openapi.Response(description="Failed to retrieve records")
        },
        operation_summary="AI Smart View"
    )
    def list(self, request):
        plant_id = request.query_params.get('plant_id')
        defect_id = request.query_params.get('defect_id')

        if not plant_id or not defect_id:
            return Response({'error': 'plant_id and defect_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant_id = int(plant_id)
            defect_id = int(defect_id)
        except ValueError:
            return Response({'error': 'plant_id and defect_id must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        model = self.MODEL_MAPPING.get(plant_id)
        if not model:
            return Response({'error': 'Invalid plant_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

        records = model.objects.filter(defects_id=defect_id).select_related('machines').order_by('-recorded_date_time').values('image', 'recorded_date_time', 'machines__name')

        # Rename 'machines__name' to 'machine_name' in the result
        results = [
            {
                'image': record['image'],
                'recorded_date_time': record['recorded_date_time'],
                'machine_name': record['machines__name']
            }
            for record in records
        ]

        return Response({"results": results}, status=status.HTTP_200_OK)
    

class MachineTemperaturesAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: MachineTemperaturesSerializer(many=True)},
    )
    def get(self, request):
        try:
            plant_id = request.query_params.get('plant_id')
            if plant_id:
                machine_ids = MachineTemperatures.objects.filter(plant_id=plant_id).values_list('machine_id', flat=True).distinct()
            else:
                machine_ids = MachineTemperatures.objects.values_list('machine_id', flat=True).distinct()

            latest_records = []
            for machine_id in machine_ids:
                if plant_id:
                    latest_record = MachineTemperatures.objects.filter(machine_id=machine_id, plant_id=plant_id).latest('recorded_date_time')
                else:
                    latest_record = MachineTemperatures.objects.filter(machine_id=machine_id).latest('recorded_date_time')

                serializer = MachineTemperaturesSerializer(latest_record)
                latest_records.append(serializer.data)

            return Response(latest_records)
        except MachineTemperatures.DoesNotExist:
            return Response({"message": "No machine records found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=MachineTemperaturesSerializer, responses={201: MachineTemperaturesSerializer})
    def post(self, request):
        serializer = MachineTemperaturesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MachineTemperatureGraphView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('machine_id', openapi.IN_QUERY, description="Machine ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: MachineTemperaturesSerializer(many=True)},
    )
    def get(self, request):
        machine_id = request.query_params.get('machine_id')
        plant_id = request.query_params.get('plant_id')

        filters = {}
        if machine_id:
            filters['machine_id'] = machine_id
        if plant_id:
            filters['plant_id'] = plant_id

        all_records = MachineTemperatures.objects.filter(**filters)

        serializer = MachineTemperaturesSerializer(all_records, many=True)
        return Response(serializer.data)


class MachineParametersGraphView(APIView):
    def get_date_only(self, date_time_str):
        date_time = datetime.fromisoformat(date_time_str)
        date_only = date_time.date()
        date_only_str = date_only.isoformat()
        return date_only_str

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Response(description="Machine Parameters Graph", examples={
            "application/json": [
                {
                    "date_time": "2024-06-13",
                    "defect_percentage": 10.5
                },
                {
                    "date_time": "2024-06-14",
                    "defect_percentage": 20.0
                }
            ]
        })}
    )
    def get(self, request):
        plant_id = request.query_params.get('plant_id')

        filters = {}
        if plant_id:
            filters['plant_id'] = plant_id

        # Filter the queryset based on the plant_id only
        parameters_graph = MachineParametersGraph.objects.filter(**filters)
        
        # Aggregating counts per day
        date_aggregates = defaultdict(lambda: {'defect_count': 0, 'total_production_count': 0})
        
        for graph in parameters_graph:
            date_only_str = graph.recorded_date_time[:10]  # Extracting date part
            if graph.machine_parameter.parameter == "Reject Counter":
                date_aggregates[date_only_str]['defect_count'] += int(graph.params_count)
            elif graph.machine_parameter.parameter in ["Program Counter", "Machine Counter"]:
                date_aggregates[date_only_str]['total_production_count'] += int(graph.params_count)
        
        data = []
        for date_only_str, counts in date_aggregates.items():
            defect_count = counts['defect_count']
            total_production_count = counts['total_production_count']
            
            if total_production_count > 0:
                defect_percentage = (defect_count / total_production_count) * 1000000
            else:
                defect_percentage = 0
            
            data.append({
                "date_time": date_only_str,
                "defect_percentage": round(defect_percentage, 2)
            })

        # Order the data by date
        data = sorted(data, key=lambda x: datetime.fromisoformat(x['date_time']))

        return Response({"results": data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['params_count', 'recorded_date_time', 'parameter', 'plant_id'],
        properties={
            'params_count': openapi.Schema(type=openapi.TYPE_STRING, description='Parameters count'),
            'recorded_date_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Recorded date and time'),
            'parameter': openapi.Schema(type=openapi.TYPE_INTEGER, description='Parameter ID'),
            'plant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Plant ID'),
        },
    ), responses={201: 'Created', 400: 'Bad Request', 404: 'Not Found'})

    def post(self, request):
        # Extract relevant data from the request and create or update a MachineParametersGraph object
        params_count = request.data.get('params_count')
        print('here')
        date_time_str = request.data.get('recorded_date_time')
        parameter_id = request.data.get('parameter')  # Assuming parameter_id is provided
        plant_id = request.data.get('plant_id')

        try:
            # Fetch the MachineParameters instance corresponding to the provided parameter_id
            parameter = MachineParameters.objects.get(pk=parameter_id)
            # Convert the given date_time to date only
            date_only_str = self.get_date_only(date_time_str)
            
            # Retrieve the existing record with the same date and parameter
            existing_graph = MachineParametersGraph.objects.filter(
                recorded_date_time__startswith=date_only_str, 
                machine_parameter=parameter,
                plant_id=plant_id
            ).first()

            if existing_graph:
                print('existing',existing_graph)
                # Update the existing record's params_count by adding the new value to the existing value
                existing_graph.params_count = F('params_count') + int(params_count)
                existing_graph.save(update_fields=['params_count'])  # Ensure that the field is updated in the database
                return Response({'message': 'MachineParametersGraph updated successfully'}, status=status.HTTP_200_OK)
            else:
                # Create a new MachineParametersGraph object
                graph = MachineParametersGraph.objects.create(
                    machine_parameter=parameter,
                    params_count=params_count,
                    recorded_date_time=date_time_str,
                    plant_id=plant_id
                )
                return Response({'message': 'MachineParametersGraph created successfully'}, status=status.HTTP_201_CREATED)
        except MachineParameters.DoesNotExist:
            return Response({'error': 'MachineParameters not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class DefectNotificationAPIView(viewsets.ViewSet):
    queryset = DefectNotification.objects.all()
    serializer_class = DefectNotificationSerializer

    @swagger_auto_schema(
        operation_summary='List All Notifications',
        manual_parameters=[
            openapi.Parameter(
                'plant_id',
                openapi.IN_QUERY,
                description="ID of the plant to filter notifications",
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    def list(self, request):
        plant_id = request.query_params.get('plant_id')
        if plant_id:
            queryset = self.queryset.filter(plant_id=plant_id).order_by('-recorded_date_time')
        else:
            queryset = self.queryset.none()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'results': serializer.data})



######### System status api ###########


class SystemStatusAPIView(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_description="Update the system status of a machine for a given plant.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'machine_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the machine'),
                'plant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plant'),
                'system_status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='System status to set'),
            },
            required=['machine_id', 'plant_id', 'system_status']
        ),
        responses={
            200: SystemStatusSerializer,
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def create(self, request, *args, **kwargs):
        machine_id = request.data.get('machine_id')
        plant_id = request.data.get('plant_id')
        system_status_value = request.data.get('system_status')

        if not machine_id or not plant_id or system_status_value is None:
            return Response({'message': 'Machine ID, Plant ID, and System Status are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            machine = Machines.objects.get(id=machine_id)
            plant = Plant.objects.get(id=plant_id)
        except Machines.DoesNotExist:
            return Response({'message': 'Machine not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Plant.DoesNotExist:
            return Response({'message': 'Plant not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the SystemStatus record exists
        system_status, created = SystemStatus.objects.get_or_create(
            machine=machine,
            plant=plant,
            defaults={'system_status': system_status_value}  # Set the initial status if the record is created
        )

        if not created:
            # Update the system status if the record already exists
            system_status.system_status = system_status_value
            system_status.save()

        serializer = SystemStatusSerializer(system_status)
        return Response({"message":"System status updated successfully."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Retrieve system statuses for a specific plant based on plant_id.",
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="ID of the plant", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="System statuses retrieved successfully",
                schema=SystemStatusSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "machine": 1,
                            "plant": 1,
                            "system_status": True
                        },
                        {
                            "machine": 2,
                            "plant": 1,
                            "system_status": False
                        }
                    ]
                }
            ),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def list(self, request):
        plant_id = request.query_params.get('plant_id')

        if not plant_id:
            return Response({'message': 'plant_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant = Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return Response({'message': 'Plant not found.'}, status=status.HTTP_404_NOT_FOUND)

        system_statuses = SystemStatus.objects.filter(plant=plant).select_related('machine')
        serializer = SystemStatusSerializer(system_statuses, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)



@method_decorator(csrf_exempt, name='dispatch')
class DefectVSProduction(viewsets.ViewSet):

    MODEL_MAPPING = {
        2: NMBDashboard,
        3: LiquidPlant,
        4: ShampooPlant,
    }

    @swagger_auto_schema(
        operation_description="List total number of defects and machine parameters (Machine Counter) for a specific plant for the current day and last 7 days",
        manual_parameters=[
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="ID of the plant", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="Data retrieved successfully",
                examples={
                    "application/json": {
                        "plant_id": 2,
                        "data_last_7_days": [
                            {
                                "date": "2024-07-10",
                                "total_defects": 10,
                                "machine_parameters": {
                                    "params_count": "5"  # Use machine_counter here
                                }
                            },
                            {
                                "date": "2024-07-09",
                                "total_defects": 5,
                                "machine_parameters": {
                                    "params_count": "3"  # Use machine_counter here
                                }
                            },
                            # other days...
                        ],
                        "today": {
                            "total_defects": 8,
                            "machine_parameters": {
                                "params_count": "2"  # Use machine_counter here
                            }
                        }
                    }
                }
            ),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def list(self, request):
        plant_id = request.query_params.get('plant_id')

        if not plant_id:
            return Response({'error': 'plant_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate if the provided plant_id is valid
        model_class = self.MODEL_MAPPING.get(int(plant_id))
        if not model_class:
            return Response({'error': 'Invalid plant_id'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Calculate date range for today and last 7 days
            today = date.today()
            date_range = [(today - timedelta(days=i)).isoformat() for i in range(7)]

            # Query total defects and machine parameters for each day
            data_last_7_days = []
            for date_str in date_range:
                # Query total defects for the current day
                total_defects = model_class.objects.filter(
                    plant_id=plant_id,
                    recorded_date_time__startswith=date_str
                ).count()

                # Query machine parameters (Machine Counter) for the current day
                machine_parameters = MachineParametersGraph.objects.filter(
                    plant_id=plant_id,
                    machine_parameter__parameter='Machine Counter',
                    recorded_date_time__startswith=date_str
                ).first()
                params_count = machine_parameters.params_count if machine_parameters else 0

                # Append data for the current day to the list
                data_last_7_days.append({
                    'date': date_str,
                    'total_defects': total_defects,
                    'total_production': params_count
                    
                })

            # Query total defects and machine parameters (Machine Counter) for today
            start_of_today = today.isoformat()

            total_defects_today = model_class.objects.filter(
                plant_id=plant_id,
                recorded_date_time__startswith=start_of_today
            ).count()

            machine_parameters_today = MachineParametersGraph.objects.filter(
                plant_id=plant_id,
                machine_parameter__parameter='Machine Counter',
                recorded_date_time__startswith=start_of_today
            ).first()
            params_count_today = machine_parameters_today.params_count if machine_parameters_today else 0

            return Response({
                'plant_id': plant_id,
                'data_last_7_days': data_last_7_days,
                'today': {
                    'total_defects': total_defects_today,
                    'total_production': params_count_today
                    
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)