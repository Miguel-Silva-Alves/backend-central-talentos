from rest_framework import routers

def getRouter():
    # middleware
    return routers.DefaultRouter(trailing_slash=False)