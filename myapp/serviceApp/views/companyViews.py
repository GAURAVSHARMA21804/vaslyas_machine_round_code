from rest_framework.views import APIView 
from ..serializers import CompanyListSerializer, CompanyDetailSerializer
from ..models.companyModel import Company
from rest_framework.response import Response
from rest_framework import status

class CompanyListView(APIView):
    def get(self, request,*args,**kwargs):
        try:
            industry = request.query_params.get('industry', None)
            print(industry)
            state = request.query_params.get('state', None)
            print(state)
            limit = request.query_params.get('limit', None)
            print(limit)

            companies = Company.objects.filter(industry=industry, state=state)[:limit]
            print(companies)

            if not companies:
                return Response({'error': 'No companies found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CompanyListSerializer(companies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyDetailView(APIView):
    def get(self, request, pk):
        try:
            company = Company.objects.get(id=pk)
            serializer = CompanyDetailSerializer(company)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
