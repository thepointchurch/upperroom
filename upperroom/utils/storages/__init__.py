from django.core.files import File

try:
    from storages.backends.s3boto3 import S3Boto3StorageFile
except ModuleNotFoundError:

    class S3Boto3StorageFile(File):
        pass


def is_s3_file(file_object):
    try:
        return isinstance(file_object.file, S3Boto3StorageFile)
    except FileNotFoundError:
        return False


def delete_s3_file(file_object):
    file_object.storage.delete(file_object.name)
