import numpy as np
from scipy.optimize import minimize

# def _rssi_to_dist(rssi):
#     if rssi >= 0:
#         return 0.5
#     return min(MAX_RANGE_M, 10.0 ** ((TX_POWER - rssi) / (10.0 * PATH_LOSS_N)))

def estimate_location(signals: list[tuple[float, float, float]]) -> tuple[float, float]:
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