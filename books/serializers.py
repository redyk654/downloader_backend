from rest_framework import serializers # type: ignore
from .models import Book, DownloadOperation



class DownloadOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadOperation
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'