from rest_framework import serializers
from .models import Questions, Answers, Comments, Favorites, Rates
from django.db.models import Avg
from likes import services as likes_services



class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Questions
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        return Questions.objects.create(author=author, **validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        action = self.context.get('action')
        if action == 'retrieve':
            representation['answer'] = AnswerSerializer(instance.answer.all(), many=True).data
        elif action == 'list':
            representation['answer'] = instance.answer.count()
        return representation


class AnswerSerializer(serializers.ModelSerializer):
    is_fan = serializers.SerializerMethodField()

    class Meta:
        model = Answers
        fields = (  "id",
                    "is_fan",
                    "created_at",
                    "text",
                    "image",
                    "question",
                    "author",
                    "total_likes",
                    )



    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        print(dir(Answers))
        return Answers.objects.create(author=author, **validated_data)

    def get_is_fan(self, obj):

        user = self.context.get('request').user
        return likes_services.is_fan(obj ,user)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        action = self.context.get('action')
        if action == 'retrieve':
            representation['comment'] = CommentSerializer(instance.comment.all(), many=True).data 
            representation['rate'] = RateSerializer(instance.rate.all(), many=True).data
        elif action == 'list':
            representation['comment'] = instance.comment.count()
            representation['rate'] = RateSerializer(instance.rate.all(), many=True).data
        if instance.rate.count()==0:
            pass
        elif instance.rate.count()>=2:
            representation['rate']= instance.rate.aggregate(Avg('rate'))
        return representation






class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        return Comments.objects.create(author=author, **validated_data)


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rates
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        return Rates.objects.create(user=user, **validated_data)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:

        model = Favorites
        fields = '__all__'

    def create(self, validated_data):
        requests = self.context.get('request')
        user = requests.user
        return Favorites.objects.create(user=user, **validated_data)