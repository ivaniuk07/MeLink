from django.db import transaction
from rest_framework import serializers

from .models import Link, Profile


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["title", "url", "sort_order"]


class ProfileSerializer(serializers.ModelSerializer):
    links = LinkSerializer(source="visible_links", many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "name",
            "short_bio",
            "about_me",
            "address",
            "photo_path",
            "theme",
            "links",
        ]


class LinkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["title", "url"]


class ProfileCreateSerializer(serializers.ModelSerializer):
    links = LinkCreateSerializer(many=True, required=False)

    class Meta:
        model = Profile
        fields = [
            "name",
            "short_bio",
            "about_me",
            "address",
            "photo_path",
            "theme",
            "links",
        ]

    def validate_links(self, value):
        if len(value) > 20:
            raise serializers.ValidationError("Можна додати не більше 20 посилань.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        links_data = validated_data.pop("links", [])
        profile = Profile.objects.create(**validated_data)

        for sort_order, link_data in enumerate(links_data, start=1):
            Link.objects.create(
                profile=profile,
                sort_order=sort_order,
                **link_data,
            )

        return profile
