from django.urls import path, include
from .api import router, ShiftScheduleView

urlpatterns = [
    path('', include(router.urls)),
    path('schedule/shift/', ShiftScheduleView.as_view(), name='api_schedule_shift'),
] 