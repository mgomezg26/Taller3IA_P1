import os
from django.conf import settings
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Assign images from media/movie/images/ to movies and update the database"

    def handle(self, *args, **kwargs):
        # ✅ Folder where the images are stored
        images_folder = os.path.join(settings.MEDIA_ROOT, 'movie', 'images')
        if not os.path.isdir(images_folder):
            self.stderr.write(f"Images folder not found: {images_folder}")
            return

        # ✅ Map filename without extension -> filename (e.g. "m_La captura" -> "m_La captura.png")
        images = {
            os.path.splitext(filename)[0]: filename
            for filename in os.listdir(images_folder)
        }

        # ✅ Fetch all movies
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        updated_count = 0
        for movie in movies:
            # ✅ Images follow the pattern m_<title>.<ext>
            filename = images.get(f"m_{movie.title}")
            if not filename:
                self.stderr.write(f"No image found for: {movie.title}")
                continue

            # ✅ Update database with the relative path
            movie.image = f"movie/images/{filename}"
            movie.save()
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))

        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movies."))
