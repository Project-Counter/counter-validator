import hashlib
from typing import IO

from django.conf import settings


def create_hasher():
    match settings.HASHING_SALT:
        case str(x):
            salt = x.encode("utf-8")
        case x:
            salt = x
    return hashlib.blake2b(digest_size=settings.HASHING_DIGEST_SIZE, salt=salt[:16])


def checksum_fileobj(fileobj: IO) -> (str, int):
    """
    Calculate the checksum of a file object. Returns the checksum and the size of the file.
    """
    orig_pos = fileobj.tell()
    fileobj.seek(0)
    hasher = create_hasher()
    size = 0
    while chunk := fileobj.read(1024 * 1024):
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        hasher.update(chunk)
        size += len(chunk)
    fileobj.seek(orig_pos)
    return hasher.hexdigest(), size


def checksum_string(string: str) -> str:
    """
    Calculate the checksum of a string.
    """
    hasher = create_hasher()
    hasher.update(string.encode("utf-8"))
    return hasher.hexdigest()
