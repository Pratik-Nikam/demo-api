from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .models import UserMaster,ActivityMaster
from collections import OrderedDict
from .serializers import UserMasterSerializer,ActivityMasterSerializer
import pandas as pd


# Create your views here.
class GenericView(generics.ListAPIView):
    """
    Generic class desigend to accept models and serializers from URL's
    Class returns query
    """
    # queryset = ActivityMaster.objects.all()
    # serializer_class = ActivityMasterSerializer
    def dispatch(self,request,*args, **kwargs):
        ModelName = kwargs.get("model", None)
        SerializerClass = kwargs.get("serializer_class", None)
        self.model= ModelName
        self.serializer_class = SerializerClass
        return super().dispatch(request,  *args, **kwargs)

    def get_queryset(self):
        """
        This functiom is used to filter data based on params received in URL.
        Below queryset fetch related data from User Model and returns all the object of passed model from URL
        """
        queryset = self.model.objects.filter(user__in = UserMaster.objects.all())
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        List function modified the serialized data from queryset as per representation require in API response.
        """
        queryset = self.get_queryset()
        
        serializer = self.get_serializer(queryset, many=True) #serialize the queryset
        info = serializer.data #parsing serizlize data to modify its structural representaion 
        
        df = pd.DataFrame(info)
        df['user'] = df['user'].apply(lambda x: dict(eval(str(x))))
        user_list = uniq_list = (df['user'].tolist())
        uniq_list = [dict(t) for t in {tuple(d.items()) for d in user_list}]
        members = []

        for i in uniq_list:
            temp_df = df[df['user'] == i]
            temp_df.reset_index(drop=True,inplace=True)
            new_resp = temp_df.loc[0,'user']
            activity_periods = []
            for x in range(len(temp_df)):
                temp_dict = {"start_time":temp_df.loc[x,'start_time'],"end_time":temp_df.loc[x,'end_time']}
                activity_periods.append(temp_dict)
            new_resp['activity_periods'] = activity_periods
            members.append(new_resp)

        if len(info) == 0:
            response_data = \
                    {
                        "Name": "DempAPI",
                        "Summary": "Disply User details with Activity Timinings",
                        "URL": f"https://creditpulseapi.decimalpointanalytics.com{request.get_full_path()}",
                        "Results":{
                                "Copyright": "Copyright (c) 2019 Decimal Point Analytics Pvt.Ltd.",
                                "Message": "Failure",
                                'Information': "Something went wrong",
                        }
                    }
            return Response(response_data)
        else:           
            response_data = \
                    {
                        "Name": "Demo API",
                        "Summary": "Disply User details with Activity Timinings",
                        "URL": f"https://demoapi.com{request.get_full_path()}",                       
                        "Message": "Success",
                        'MembersInfo': members,                 
                    }
            return Response(response_data)