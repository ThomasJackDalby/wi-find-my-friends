import numpy as np
import socket
import requests
from scipy.optimize import minimize

SCAN_PERIOD   = 1.0
TX_POWER      = -40
PATH_LOSS_N   = 2.8
MAX_RANGE_M   = 30.0

def rssi_to_dist(rssi):
    if rssi >= 0: return 0.5
    return min(MAX_RANGE_M, 10.0 ** ((TX_POWER - rssi) / (10.0 * PATH_LOSS_N)))

def estimate_location(signals: list[tuple[float, float, float]]) -> tuple[float, float]:
    """
    Estimates the position based on signals received.

    Returns:
        tuple[float, float]: A tuple of the x, y position (e.g. (1.23, 4.56))
    """
    anchors = np.array([[s[0], s[1]] for s in signals])

    def localization_loss(position, anchors, measured_distances):
        hypothesized_distances = np.linalg.norm(anchors - position, axis=1)
        residuals = hypothesized_distances - measured_distances
        return np.sum(residuals**2)

    initial_guess = np.mean(anchors, axis=0)
    result = minimize(
        fun=localization_loss,
        x0=initial_guess,
        args=(anchors, np.array([s[2] for s in signals])),
        method='BFGS' # Broyden–Fletcher–Goldfarb–Shanno algorithm
    )
    return result.x

def get_local_ip():
    """
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80)) # Doesn't have to be reachable
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

def get_external_ip() -> str:
    """
    Retrieves the public IP address of the host machine.

    Queries an external IP lookup service to determine the current public-facing 
    IPv4 address and returns it as a standard dot-separated string.

    Returns:
        str: The public IP address (e.g., '192.0.2.1').

    Raises:
        requests.RequestException: If the network request to the external 
            API fails or times out.
        ValueError: If the retrieved response is not a valid IPv4 address.
    """
    response = requests.get('https://api.ipify.org').text
    # TODO: assert the text is of the correct form
    return response