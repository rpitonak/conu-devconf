from conu import DockerBackend


def check_container_port(image):
    """
    run container and wait for successful
    response from the service exposed via port 8080
    """
    port = 8080
    container = image.run_via_binary()
    container.wait_for_port(port)

    # check httpd runs
    http_response = container.http_request(port=port)
    assert http_response.ok

    # cleanup
    container.delete(force=True)
