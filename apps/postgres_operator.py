from transpire import helm
from transpire.resources import Secret
from transpire.utils import get_versions

name = "postgres-operator"


def objects():
    s3_secret = "storage-s3-key"
    yield Secret(
        name=s3_secret,
        string_data={
            "STORAGE_S3_ACCESS_KEY_ID": "",
            "STORAGE_S3_SECRET_ACCESS_KEY": "",
        },
    ).build()

    yield from helm.build_chart_from_versions(
        name=name,
        versions=get_versions(__file__),
        values={
            "image": {
                "tag": "v1.8.2-43-g3e148ea5",
            },
        },
    )

    yield {
        "apiVersion": "acid.zalan.do/v1",
        "kind": "postgresql",
        # name must be in {TEAM}-{NAME} format
        "metadata": {"name": "ocf-postgres-nvme"},
        "spec": {
            "teamId": "ocf",
            "volume": {
                "size": "512Gi",
                "storageClass": "rbd-nvme",
            },
            "numberOfInstances": 1,
            "postgresql": {"version": "14"},
            # https://thedatabaseme.de/2022/03/26/backup-to-s3-configure-zalando-postgres-operator-backup-with-wal-g/
            "env": list(map(lambda pair: {"name": pair[0], "value": pair[1]}, {
                "WAL_S3_BUCKET": "ocf-postgres-backup",
                "WAL_BUCKET_SCOPE_PREFIX": "",
                "WAL_BUCKET_SCOPE_SUFFIX": "",
                "USE_WALG_BACKUP": "true",
                "USE_WALG_RESTORE": "true",
                'BACKUP_SCHEDULE': '00 10 * * *',
                "AWS_S3_FORCE_PATH_STYLE": "true",
                "AWS_ENDPOINT": "https://o3.ocf.io",
                "AWS_REGION": "rgw-hdd",
                "WALG_DISABLE_S3_SSE": "false",
                "BACKUP_NUM_TO_RETAIN": "5",
                "CLONE_USE_WALG_RESTORE": "true"
            }.items())) + [
                       {"name": "AWS_ACCESS_KEY_ID", "valueFrom": {
                           "secretKeyRef": {
                               "name": s3_secret,
                               "key": "STORAGE_S3_ACCESS_KEY_ID"
                           }
                       }},
                       {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": {
                           "secretKeyRef": {
                               "name": s3_secret,
                               "key": "STORAGE_S3_SECRET_ACCESS_KEY"
                           }
                       }}
                   ]
        },
    }
