from rest_framework.response import Response
from api.permission import TokenAuth
from rest_framework.views import APIView

from users.models import User
from codes.models import Code
from codes.serializer import CodeSerializer


class CodesList(APIView):
    permission_classes = (TokenAuth,)
    serializer_class = CodeSerializer

    def get(self, request):
        try:
            if request.GET.get('liked_by'):
                codes = Code.objects.filter(liked_by__hash=request.GET.get('liked_by'))
                serializer = CodeSerializer(codes, many=True)
                return Response(serializer.data, status=200)
            elif request.GET.get('sort'):
                if request.GET.get('sort') == 'viewed':
                    codes = Code.objects.order_by('-views')
                    serializer = CodeSerializer(codes, many=True)
                    return Response(serializer.data, status=200)
                elif request.GET.get('sort') == 'liked':
                    codes = Code.objects.order_by('-liked_by')
                    serializer = CodeSerializer(codes, many=True)
                    return Response(serializer.data, status=200)
                else:
                    return Response({"error": "Sort accept viewed or liked"}, status=400)
            else:
                codes = Code.objects.all()
                serializer = CodeSerializer(codes, many=True)
                return Response(serializer.data, status=200)
        except Code.DoesNotExist:
            return Response({"error": "No codes found"}, status=404)

    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CodesDetail(APIView):
    permission_classes = (TokenAuth,)
    serializer_class = CodeSerializer

    def get(self, request, token_id):
        try:
            code = Code.objects.get(token_id=token_id)
            serializer = CodeSerializer(code)
            code.views += 1
            code.save()
            return Response(serializer.data, status=200)
        except Code.DoesNotExist:
            serializer = CodeSerializer(data={'token_id': token_id})
            if serializer.is_valid():
                serializer.save()
                code = Code.objects.get(token_id=token_id)
                code.views += 1
                code.save()
                return Response({"success": True}, status=201)
            return Response(serializer.errors, status=400)
    #
    # def put(self, request, token_id, format=None):
    #     try:
    #         code = Code.objects.get(token_id=token_id)
    #         for key, value in request.data.items():
    #             if not hasattr(code, key):
    #                 return Response({"error": "Key does not exist"}, status=400)
    #             setattr(code, key, value)
    #         code.save()
    #         serializer = CodeSerializer(code)
    #         return Response(serializer.data, status=200)
    #     except Code.DoesNotExist:
    #         return Response({"error": "Code does not exist"}, status=404)


class LikeCodes(APIView):
    permission_classes = (TokenAuth,)
    serializer_class = CodeSerializer

    def get(self, request, token_id):
        try:
            code = Code.objects.get(token_id=token_id)
            code.liked_by.count()
            return Response({"liked": code.liked_by.count()}, status=200)
        except Code.DoesNotExist:
            return Response({"error": "Code does not exist"}, status=404)

    def post(self, request, token_id):
        try:
            code = Code.objects.get(token_id=token_id)
            if code.liked_by.contains(request.user):
                return Response({"error": "Already liked"}, status=409)
            code.liked_by.add(request.user)
            code.save()
            return Response({"success": True}, status=201)
        except Code.DoesNotExist:
            serializer = CodeSerializer(data= {'token_id': token_id})
            if serializer.is_valid():
                serializer.save()
                code = Code.objects.get(token_id=token_id)
                code.liked_by.add(request.user)
                code.save()
                return Response({"success": True}, status=201)
            return Response(serializer.errors, status=400)

    def delete(self, request, token_id):
        try:
            code = Code.objects.get(token_id=token_id)
            if not code.liked_by.contains(request.user):
                return Response({"error": "Not liked"}, status=409)
            code.liked_by.remove(request.user)
            code.save()
            serializer = CodeSerializer(code)
            return Response(serializer.data, status=200)
        except Code.DoesNotExist:
            return Response({"error": "Code does not exist"}, status=404)
