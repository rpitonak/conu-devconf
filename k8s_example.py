from conu import K8sBackend
from conu import DockerBackend
from conu.backend.k8s.pod import Pod, PodPhase
from conu.utils import get_oc_api_token


def test_pod():
    api_key = get_oc_api_token()
    with K8sBackend(api_key=api_key) as k8s_backend:

        namespace = k8s_backend.create_namespace()

        with DockerBackend() as backend:
            image = backend.ImageClass("openshift/hello-openshift")

            pod = image.run_in_pod(namespace=namespace)

            try:
                pod.wait(200)
                assert pod.is_ready()
                assert pod.get_phase() == PodPhase.RUNNING
            finally:
                pod.delete()
                assert pod.get_phase() == PodPhase.TERMINATING
                k8s_backend.delete_namespace(namespace)


def test_pod_from_template():
    template = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "myapp-pod",
            "labels": {
                "app": "myapp"
            }
        },
        "spec": {
            "containers": [
                {
                    "name": "myapp-container",
                    "image": "busybox",
                    "command": [
                        "sh",
                        "-c",
                        "echo Hello Kubernetes! && sleep 3600"
                    ]
                }
            ]
        }
    }

    api_key = get_oc_api_token()
    with K8sBackend(api_key=api_key) as k8s_backend:

        pod = Pod(namespace='myproject', from_template=template)

        try:
            pod.wait(200)
            assert pod.is_ready()
            assert pod.get_phase() == PodPhase.RUNNING
        finally:
            pod.delete()
            assert pod.get_phase() == PodPhase.TERMINATING


test_pod_from_template()
