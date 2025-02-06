'''
functions for determining the Blomberg's K phylogenetic signal metric

References
---------
Blomberg, Simon P., Theodore Garland, and Anthony R. Ives. 
“TESTING FOR PHYLOGENETIC SIGNAL IN COMPARATIVE DATA: BEHAVIORAL TRAITS ARE MORE LABILE.” 
Evolution 57, no. 4 (April 2003): 717–45. https://doi.org/10.1111/j.0014-3820.2003.tb00285.x.


'''
import numpy as np
import toytree





def compute_D(V):
    """
    Computes the transformation matrix D such that D V D' = I.
    """
    # Compute the inverse square root of V using eigendecomposition
    eigvals, eigvecs = np.linalg.eigh(V)  # Eigen decomposition of V
    Lambda_sqrt_inv = np.diag(1.0 / np.sqrt(eigvals))  # Inverse sqrt of eigenvalues
    D = Lambda_sqrt_inv @ eigvecs.T  # Compute D

    return D

def generalized_least_squares(X, V):
    """
    Computes the phylogenetic mean (a_hat) and residual variance (MSE)
    using Generalized Least Squares (GLS).
    """
    n = len(X)
    D = compute_D(V)  # Compute the transformation matrix D

    # Step 2: Transform X
    U = D @ X

    # Step 3: Compute phylogenetic mean
    a_hat = np.mean(U)

    # Step 4: Compute residual variance (MSE)
    residuals = U - a_hat
    MSE = (residuals.T @ residuals) / n

    return a_hat, MSE

def calculate_blomberg_k(tree, data):
    V = tree.pcm.get_vcv_matrix_from_tree()
    n = tree.ntips

    # Compute GLS phylogenetic mean and MSE
    a_hat, MSE = generalized_least_squares(data, V)

    # Compute observed MSE_0
    residuals_0 = data - a_hat
    MSE_0 = (residuals_0.T @ residuals_0) / (n - 1)

    # Compute expected MSE under Brownian motion
    V_inv = np.linalg.inv(V)
    expected_MSE = (1 / (n - 1)) * ((np.trace(V) - n / (np.sum(V_inv))))

    # Compute Blomberg's K
    K = (MSE_0 / MSE) / expected_MSE
    return K

if __name__ == "__main__":

    tree = toytree.rtree.rtree(10)
    #purposefully high signal
    tip_data_1 = np.array([3.45, 6.78, 7.32, 16.43, 16.94, 25.56, 35.66, 37.55, 67.43, 68.78]) 
    mu, sigma = 0, 0.1 
    #random data (should be low signal)
    tip_data_2 = np.random.normal(mu, sigma, 10) 

    print(calculate_blomberg_k(tree, tip_data_1))
    print(calculate_blomberg_k(tree, tip_data_2))