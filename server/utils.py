import numpy as np
from scipy.optimize import minimize


def _rssi_to_dist(rssi):
    if rssi >= 0:
        return 0.5
    return min(MAX_RANGE_M, 10.0 ** ((TX_POWER - rssi) / (10.0 * PATH_LOSS_N)))

def main():

    # 1. Define the known static anchor positions (X, Y)
    # You can add as many anchors as you like; minimum 3 for 2D triangulation.
    anchors = np.array([
        [0.0, 0.0],    # Anchor A
        [10.0, 0.0],   # Anchor B
        [5.0, 10.0],   # Anchor C
        [0.0, 10.0]    # Anchor D
    ])

    # 2. Simulate a true object position and noisy distance measurements
    true_position = np.array([4.2, 6.7])

    # Calculate true distances
    true_distances = np.linalg.norm(anchors - true_position, axis=1)

    # Add Gaussian noise to simulate real-world sensor inaccuracies
    np.random.seed(42)  # For reproducible results
    noise_std = 0.3     # Standard deviation of noise in meters/units
    noisy_distances = true_distances + np.random.normal(0, noise_std, size=len(true_distances))

    # 3. Define the Loss Function (Residuals)
    def localization_loss(position, anchors, measured_distances):
        """
        Calculates the sum of squared errors between the hypothesized 
        distances and the actual measured distances.
        """
        # Calculate Euclidean distance from the current guess to all anchors
        hypothesized_distances = np.linalg.norm(anchors - position, axis=1)
        
        # Calculate the residuals (errors)
        residuals = hypothesized_distances - measured_distances
        
        # Return the sum of squared errors
        return np.sum(residuals**2)

    # 4. Run the Optimization
    # Start with an initial guess (e.g., the average of all anchor positions)
    initial_guess = np.mean(anchors, axis=0)

    result = minimize(
        fun=localization_loss,
        x0=initial_guess,
        args=(anchors, noisy_distances),
        method='BFGS' # Broyden–Fletcher–Goldfarb–Shanno algorithm
    )

    # 5. Display the Results
    estimated_position = result.x

    print("--- Triangulation Results ---")
    print(f"True Position:       {true_position}")
    print(f"Initial Guess:       {initial_guess}")
    print(f"Estimated Position:  {estimated_position}")
    print(f"Absolute Error:      {np.linalg.norm(estimated_position - true_position):.4f} units")
    print(f"Optimization Success: {result.success}")