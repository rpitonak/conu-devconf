from conu.utils import get_oc_api_token
from conu import OpenshiftBackend


def test_deploy_image():
    api_key = get_oc_api_token()
    with OpenshiftBackend(api_key=api_key) as openshift_backend:
        # create new app from remote source in OpenShift cluster
        app_name = openshift_backend.deploy_image("centos/mariadb-102-centos7",
                                                  oc_new_app_args=[
                                                      "--env", "MYSQL_ROOT_PASSWORD=test"],
                                                  project='myproject')

        try:
            # wait until service is ready to accept requests
            openshift_backend.wait_for_service(
                app_name=app_name,
                port=3306,
                timeout=300)
            assert openshift_backend.all_pods_are_ready(app_name)
        finally:
            openshift_backend.get_logs(app_name)
            openshift_backend.clean_project(app_name)


def test_oc_s2i_remote():
    api_key = get_oc_api_token()
    with OpenshiftBackend(api_key=api_key, logging_level=logging.DEBUG) as openshift_backend:

        openshift_backend.get_status()

        app_name = openshift_backend.create_new_app_from_source(
            "centos/python-36-centos7",
            source="https://github.com/openshift/django-ex.git",
            project="myproject")

        try:
            openshift_backend.wait_for_service(
                app_name=app_name,
                port=8080,
                expected_output='Welcome to your Django application on OpenShift',
                timeout=300)
        finally:
            openshift_backend.get_logs(app_name)
            openshift_backend.clean_project(app_name)


test_deploy_image()
test_oc_s2i_remote()

