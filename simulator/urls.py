from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



from django.contrib import admin
from django.urls import path
from openfoam.views import AddSimulationView, RunSimulationView, CreateUserView


urlpatterns = [
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/register', CreateUserView.as_view()),
    path('admin/', admin.site.urls),
    path('simulations', AddSimulationView.as_view()),
    path('run_simulation', RunSimulationView.as_view()),
]
