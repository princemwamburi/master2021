from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url('upload_dataset/',views.UploadDataset.as_view()),
    url("equipment/",views.GetEquipment.as_view()),
    path("search/<str:parcel>/",views.search_by_parcel),
    path("getParcel/<int:id>/",views.get_survey_by_id)
]
