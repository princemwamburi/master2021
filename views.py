import os
from pathlib import Path

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, JsonResponse
from rest_framework import views, generics
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from gis_bank import models
from gis_bank import serializers
from gis_bank.city2infragml import citygml2infragml
from gis_bank.shape2gml import ConvertGml
from gis_bank.shapetocity import ConvertCity


class UploadDataset(views.APIView):
    parser_classes = (MultiPartParser,)

    def put(self, request):
        request_data = request.POST.dict()
        request_data["upload_files"] = request.FILES.dict()
        request_data["upload_files"]["format"] = request_data["format"]
        serializer = serializers.SurveyDetailSerializer(data=request_data)
        if serializer.is_valid():
            upload_serializer = serializer.initial_data["upload_files"]
            folder = serializer.validated_data["purpose"].replace(" ", "_")
            out_path = os.path.join(os.getcwd(), "static", "out", folder)
            Path(out_path).mkdir(parents=True, exist_ok=True)
            for file in upload_serializer.keys():
                # file = serializer.validated_data["file"]
                if isinstance(upload_serializer[file], InMemoryUploadedFile):
                    with open(f'static/input/{upload_serializer[file].name}', 'wb') as f:
                        f.write(upload_serializer[file].read())
            shp_file_name = upload_serializer["shp_file"].name
            shp_file_name = shp_file_name[:-4]
            # out_xml = convert_to_landxml(os.path.join("static/input",shp_file_name),'ft',shp_file_name.split(".")[0])
            if upload_serializer["format"] == "reg_gml":
                out_file = ConvertGml().convert_shp(shp_file_name, folder)
                # out_city = f"{shp_file_name}_city"
                out_city_path = ConvertCity(shp_file_name, folder).build_gml_main()
                out_infra_path = os.path.join(out_path, f"{shp_file_name}_infra.gml")
                citygml2infragml(out_city_path, out_infra_path)
                resp_data = {
                    "reg_gml": {
                        "data": None,
                        "file_name": f"{shp_file_name}.gml"
                    },
                    "infra_gml": {
                        "data": None,
                        "file_name": f"{shp_file_name}`.gml"
                    }
                }
                with open(out_file, 'r') as file:
                    resp_data["reg_gml"]["data"] = file.read()
                with open(out_infra_path, 'r') as file:
                    resp_data["infra_gml"]["data"] = file.read()
                serializer.save()
                return JsonResponse(resp_data)


            else:
                out_file = ConvertCity(shp_file_name, folder).build_gml_main()
                serializer.save()
                with open(out_file, 'r') as file:
                    resp_data = {
                        "city_gml":{
                            "data":file.read(),
                            "file_name": f"{shp_file_name}.gml"
                        }
                    }
                    response = JsonResponse(resp_data)
                    return response

        else:
            return Response(status=400, data=serializer.errors)


class GetEquipment(generics.ListAPIView):
    serializer_class = serializers.EquipmentSerializer
    queryset = models.Equipment.objects.all()


@api_view(["GET"])
def get_survey_by_id(request, id):
    surve_det = models.SurveyDetail.objects.get(id=id)
    serializer = serializers.SurveyDetailSerializer(surve_det)
    folder = serializer.data["purpose"].replace(" ", "_")
    out_path = os.path.join(os.getcwd(), "static", "out", folder)
    for filename in os.listdir(out_path):
        if filename.endswith(".gml") or filename.endswith(".xml"):
            content_type = ""
            if (filename.endswith(".gml")):
                content_type = "text/gml"
            else:
                content_type = "text/xml"
            out_file = os.path.join(out_path, filename)
            with open(out_file, 'r') as file:
                response = HttpResponse(file, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename={out_file}'
                return response

    return Response(status=404)


@api_view(['GET'])
def search_by_parcel(request, parcel):
    mod = models.SurveyDetail.objects.filter(parcel_num__contains=parcel)
    serializer = serializers.SurveyDetailSerializer(mod, many=True)
    return Response(serializer.data)
