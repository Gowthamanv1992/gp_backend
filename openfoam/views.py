from django.shortcuts import render
from rest_framework.views import APIView
from simulator.constants import FILE_PATH
from rest_framework.response import Response
from multiprocessing import Process
from .models import SimulationModel, ResultsModel
from django.db import IntegrityError
from datetime import datetime
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model # If used custom user model
from rest_framework import permissions
from .serializers import UserSerializer
from subprocess import call
import json
import os
from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS, load_backend
from .openfoam import run_openfoam

OPENFOAM_PATH = ''

class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]

    serializer_class = UserSerializer

def train_ml():
    print()


def create_connection(alias=DEFAULT_DB_ALIAS):

    connections.ensure_defaults(alias)
    connections.prepare_test_settings(alias)
    db = connections.databases[alias]
    backend = load_backend(db['ENGINE'])
    return backend.DatabaseWrapper(db, alias)


def run_ml(id, rn, aoa):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    python_file = BASE_DIR + '/files/neural_network/NN_prediction.py'
    call(["python3", python_file, str(rn), str(aoa) , str(id), BASE_DIR + '/files'])

    with open(BASE_DIR + '/files/output_data/ml_output_' + str(id) + '.json') as json_file:
        data = json.load(json_file)
    
    predicted_lift = round(data['lift'],6)
    predicted_drag = round(data['drag'],6)
    ca1 = round(data['ca1'],6)
    ca2 = round(data['ca2'],6)
    ce1 = round(data['ce1'],6)
    ce2 = round(data['ce2'],6)

    conn = create_connection()
    cursor = conn.cursor()
    error_query = f'UPDATE openfoam_resultsmodel set predicted_lift={predicted_lift}, predicted_drag={predicted_drag}, ca1={ca1},ca2={ca2}, ce1 = {ce1}, ce2={ce2} WHERE id={id}'

    cursor.execute(error_query)
    conn.close()

    output_file = BASE_DIR + '/files/output_data/openfoam_output_' + str(id) + '.json'
    run_openfoam(rn, aoa, ca1, ca2, ce1, ce2, OPENFOAM_PATH, output_file)



def handle_uploaded_file(file, id):

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    with open(BASE_DIR + '/files/training_data_' + str(id) , 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

# Create your views here.

class AddSimulationView(APIView):

    def get(self, request, **kwargs):

        data = SimulationModel.objects.filter(owner=request.user)
        simulations = []
        for row in data:
            simulations.append({'name' : row.name, 'id' : row.id})

        return Response({'data' : simulations})

    def post(self, request, **kwargs):
        file_obj = request.FILES.get('file', '')
        
        name = request.POST['name']

        id = None

        try:
            model = SimulationModel.objects.create(name=name, status='created',type='RANS',owner=request.user)
            model.save()
            id = model.id

        except IntegrityError as e:
            print(e)
            return Response({'status' : 'failed'})

        # p = Process(target=train_ml, args=())
        # p.start()

        handle_uploaded_file(file_obj, id)

        model = SimulationModel.objects.get(name=name)
        model.status = 'completed'
        model.save()

        return Response({"id" : model.id, 'status' : 'success'})


class RunSimulationView(APIView):

    def get(self, request, **kwargs):
        simulation_id = request.GET['id']

        data = ResultsModel.objects.filter(simulation_id=simulation_id).order_by('-start_time')

        results = []
        for row in data:
            date_time = row.start_time.strftime("%d-%m-%Y %H:%M:%S")
            results.append({'name' : row.name, 'id' : row.id, 'ca1' : row.ca1, 'ca2' : row.ca2, 'ce1' : row.ce1, 'ce2' : row.ce2, 'predicted_lift' : row.predicted_lift, 'predicted_drag' : row.predicted_drag, 'actual_lift' : row.actual_lift, 'actual_drag' : row.actual_drag, 'aoa' : row.aoa, 're' : row.rn, 'start_time' : date_time})
        
        return Response({'data' : results})

    def post(self, request, **kwargs):
        simulation_id = request.GET['id']
        data = request.data

        result = ResultsModel.objects.create(simulation_id=simulation_id, name=data['name'], aoa=data['aoa'], rn=data['rn'], start_time=datetime.now())
        id = result.id

        p = Process(target=run_ml, args=(id, data['rn'], data['aoa']))
        p.start()

        return Response({})