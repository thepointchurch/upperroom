from django.conf import settings
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


def is_s3_file_public(file_object):
    for grant in file_object.file.obj.Acl().grants:
        if (
            grant["Permission"] == "READ"
            and grant["Grantee"]["URI"] == "http://acs.amazonaws.com/groups/global/AllUsers"
        ):
            return True
    return False


# Always True if settings.MEDIAFILES_ENCRYPTED is False
def is_s3_encrypted(file_object):
    return not settings.MEDIAFILES_ENCRYPTED or file_object.file.obj.server_side_encryption is not None


def delete_s3_file(file_object):
    file_object.storage.delete(file_object.name)


def set_s3_file_acl(file_object, acl):
    file_object.file.obj.Acl().put(ACL=acl)


def decrypt_s3_file(file_object):
    try:
        file_object.storage.save_cleartext(file_object.file.name)
    except AttributeError:
        pass
    file_object.file.content_type = file_object.file.obj.content_type
    file_object.storage.save(file_object.file.name, file_object.file)


# Will only really encrypt if settings.MEDIAFILES_ENCRYPTED is True
def encrypt_s3_file(file_object):
    file_object.file.content_type = file_object.file.obj.content_type
    file_object.storage.save(file_object.file.name, file_object.file)
