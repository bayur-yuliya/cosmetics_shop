from storages.backends.s3boto3 import S3Boto3Storage  # noqa: I001


class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
