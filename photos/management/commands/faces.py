# -*- coding: utf-8 -*-
import cv2
import logging
from io import BytesIO
from skimage import io
from photos.models import Photo, Face
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Extract faces from LAPL photos"

    def handle(self, *args, **options):
        obj = Photo.objects.filter(faces_extracted=False).order_by("?")[0]

        print(f"Downloading {obj.image.url}")
        image = io.imread(obj.image.url)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        print("Converting to black and white")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        print("Identifing faces")
        faceCascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=2,
            minSize=(30, 30)
        )
        print(f"Found {len(faces)} Faces!")

        print("Cropping faces")
        for (x, y, w, h) in faces:
            crop = image[y:y + h, x:x + w]

            is_success, buffer = cv2.imencode(".jpg", crop)
            io_obj = BytesIO(buffer)

            face_obj = Face.objects.create(
                photo=obj,
                x=x,
                y=y,
                width=w,
                height=h
            )

            filename = f"{obj.lapl_id}_{face_obj.id}.jpg"
            face_obj.image.save(filename, io_obj, save=True)
            print(face_obj.image.url)

        obj.faces_extracted = True
        obj.save()
