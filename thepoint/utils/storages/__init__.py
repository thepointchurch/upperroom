try:
    from storages.backends.s3boto3 import S3Boto3StorageFile
except ModuleNotFoundError:
    from django.core.files.base import File

    class S3Boto3StorageFile(File):
        pass


def is_s3_file(file_object):
    return isinstance(file_object.file, S3Boto3StorageFile)


def is_s3_file_public(file_object):
    for grant in file_object.file.obj.Acl().grants:
        if (
            grant["Permission"] == "READ"
            and grant["Grantee"]["URI"] == "http://acs.amazonaws.com/groups/global/AllUsers"
        ):
            return True
    return False


def delete_s3_file(file_object):
    file_object.storage.delete(file_object.name)


def set_s3_file_acl(file_object, acl):
    file_object.file.obj.Acl().put(ACL=acl)
