import autograd.numpy as np
from autograd import grad

#  import numpy as np
from scipy import stats
from linear_regression_models import LinearRegression


class OrdinaryLeastSquares(LinearRegression):
    def __init__(self, degree):
        """Constructor for the ordinary least squares

        Parameters
        ----------
            degree : int
                The degree for the ordinary least squares model
        """
        super().__init__(degree)

    def fit(self, X, z):
        """Fits data using ordinary least squares saving the betas for the fit

        Parameters
        ----------
            X : np.array
                The X values for which to fit the model
            z : np.array
                The z values for which to fit the model
        """
        hessian = X.T @ X
        hessian_inv = np.linalg.pinv(hessian)
        self.beta = hessian_inv @ X.T @ z

    def loss_function(self, X, z, beta):
        """Returns the loss function for the model

        Parameters
        ----------
            X : np.array
                The X values for which to calculate the loss function
            z : np.array
                The z values for which to calculate the loss function
            beta : np.array
                The beta values for which to calculate the loss function

        Returns
        -------
            loss : float
                The loss function for the model
        """
        loss = np.mean((z.reshape(-1, 1) - X @ beta) ** 2)
        return loss

    def confidence_intervals(self, X, z, z_tilde, alpha=0.05):
        """Calculates the confidence interval for each beta value

        Parameters
        ----------
            X : np.array
                The X values for which to calculate the confidence intervals
            z : np.array
                The z values for which to calculate the confidence intervals
            z_tilde : np.array
                The z_tilde values for which to calculate the confidence intervals
            alpha : float
                The alpha value for a 1-alpha confidence interval

        Returns
        -------
            confidence_intervals : tuple(np.array, np.array)
                The 1-alpha confidence intervals for the betas
            z_times_sigma_betas : np.array
                The uncertainty of the betas
            sigma_squared : float
                The predicted sigma squared
        """
        N = len(z_tilde)
        Z = stats.norm.ppf(1 - alpha / 2)
        sigma_squared = 1 / (N - len(self.beta) - 1) * np.sum((z - z_tilde) ** 2)
        hessian = X.T @ X
        hessian_inv = np.linalg.pinv(hessian)
        sigma_betas = sigma_squared * np.sqrt(hessian_inv.diagonal())
        confidence_intervals = (
            self.beta - Z * sigma_betas,
            self.beta + Z * sigma_betas,
        )
        return confidence_intervals, Z * sigma_betas, sigma_squared

    def __repr__(self):
        """Returns the name of the model"""
        return "ols"
