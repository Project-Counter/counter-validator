import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string


class RandomFileSystemStorage(FileSystemStorage):
	def __init__(self, *args, **kwargs):
		length = kwargs.pop("length", None)
		if length is None:
			length = settings.RANDOM_FILENAME_LENGTH
		self.length = length
		super().__init__(*args, **kwargs)

	def random(self):
		return get_random_string(self.length, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

	def get_valid_name(self, *_, **__):
		return self.random()

	def get_available_name(self, name, **__):
		dir_name, file_name = os.path.split(name)
		for _ in range(3):
			if not self.exists(name):
				return name
			name = os.path.join(dir_name, self.random())
		raise RuntimeError("The impossible happened. Couldn't generate a unique filename.")


upload_storage = RandomFileSystemStorage(location=settings.UPLOAD_ROOT)
