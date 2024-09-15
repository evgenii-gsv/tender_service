from rest_framework import response, status, views


class PingView(views.APIView):

    def get(self, request):
        return response.Response('ok', status=status.HTTP_200_OK)
