import os
import subprocess

from ruamel.yaml import YAML

from ..file_acquisition import find_absolute_path_to_cluster_file, get_decrypted_file

yaml = YAML(typ="safe")


def get_grafana_url(cluster_name):
    cluster_config_dir_path = find_absolute_path_to_cluster_file(cluster_name).parent

    config_file = cluster_config_dir_path.joinpath("support.values.yaml")
    with open(config_file) as f:
        support_config = yaml.load(f)

    grafana_tls_config = (
        support_config.get("grafana", {}).get("ingress", {}).get("tls", [])
    )

    if not grafana_tls_config:
        raise ValueError(
            f"No tls config was found for the Grafana instance of {cluster_name}. Please consider enable it before using it as the central Grafana."
        )

    # We only have one tls host right now. Modify this when things change.
    return grafana_tls_config[0]["hosts"][0]


def get_cluster_prometheus_address(cluster_name):
    """Retrieves the address of the prometheus instance running on the `cluster_name` cluster.
    This address is stored in the `support.values.yaml` file of each cluster config directory.

    Args:
        cluster_name: name of the cluster
    Returns:
        string object: https address of the prometheus instance
    Raises ValueError if
        - `prometheusIngressAuthSecret` isn't configured
        - `support["prometheus"]["server"]["ingress"]["tls"]` doesn't exist
    """
    cluster_config_dir_path = find_absolute_path_to_cluster_file(cluster_name).parent

    config_file = cluster_config_dir_path.joinpath("support.values.yaml")
    with open(config_file) as f:
        support_config = yaml.load(f)

    # Don't return the address if the prometheus instance wasn't securely exposed to the outside.
    if not support_config.get("prometheusIngressAuthSecret", {}).get("enabled", False):
        raise ValueError(
            f"`prometheusIngressAuthSecret` wasn't configured for {cluster_name}"
        )

    tls_config = (
        support_config.get("prometheus", {})
        .get("server", {})
        .get("ingress", {})
        .get("tls", [])
    )

    if not tls_config:
        raise ValueError(
            f"No tls config was found for the prometheus instance of {cluster_name}"
        )

    # We only have one tls host right now. Modify this when things change.
    return tls_config[0]["hosts"][0]


def get_cluster_prometheus_creds(cluster_name):
    """Retrieves the credentials of the prometheus instance running on the `cluster_name` cluster.
    These credentials are stored in `enc-support.secret.values.yaml` file of each cluster config directory.

    Args:
        cluster_name: name of the cluster
    Returns:
        dict object: {username: `username`, password: `password`}
    """
    cluster_config_dir_path = find_absolute_path_to_cluster_file(cluster_name).parent

    config_filename = cluster_config_dir_path.joinpath("enc-support.secret.values.yaml")

    with get_decrypted_file(config_filename) as decrypted_path:
        with open(decrypted_path) as f:
            prometheus_config = yaml.load(f)

    return prometheus_config.get("prometheusIngressAuthSecret", {})


def get_central_grafana_token(cluster_name):
    """Returns the access token of the Grafana located in `cluster_name` cluster.
    This access token should have enough permissions to create datasources.
    """
    # Get the location of the file that stores the central grafana token
    cluster_config_dir_path = find_absolute_path_to_cluster_file(cluster_name).parent

    grafana_token_file = (cluster_config_dir_path).joinpath(
        "enc-grafana-token.secret.yaml"
    )

    # Read the secret grafana token file
    with get_decrypted_file(grafana_token_file) as decrypted_file_path:
        with open(decrypted_file_path) as f:
            config = yaml.load(f)

    return config["grafana_token"]


def update_central_grafana_token(cluster_name, token):
    # Get the location of the file that stores the central grafana token
    cluster_config_dir_path = find_absolute_path_to_cluster_file(cluster_name).parent

    grafana_token_file = (cluster_config_dir_path).joinpath(
        "enc-grafana-token.secret.yaml"
    )

    # If grafana token file exists delete it and then create it again with new token
    # Fastest way to update the token
    if os.path.exists(grafana_token_file):
        os.remove(grafana_token_file)

    with open(grafana_token_file, "w") as f:
        f.write(f"grafana_token: {token}")

    # Encrypt the private key
    subprocess.check_call(["sops", "--in-place", "--encrypt", grafana_token_file])
