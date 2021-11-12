import numpy as np
from linear_regression_models import LinearRegression
from generate_data import BreastCancerData


class LogisticRegression(LinearRegression):
    def __init__(self):
        pass

    def cost_function(self, X, y, lambda_):
        m = len(y)
        h = self.sigmoid(np.dot(X, self.theta))
        J = -(1 / m) * np.sum(y * np.log(h) + (1 - y) * np.log(1 - h))
        if lambda_:
            J += lambda_ / (2 * m) * np.sum(np.square(self.theta))
        return J

    def cost_function_gradient(self, X, y, lambda_):
        m = len(y)
        h = self.h(X, self.theta)
        gradient = (1 / m) * np.dot(X.T, h - y)
        if lambda_:
            gradient += (lambda_ / m) * self.theta
        return gradient

    def gradient_descent(self, X, y, alpha, iterations, lambda_):
        for _ in range(iterations):
            gradient = self.cost_function_gradient(X, y, lambda_=lambda_)
            self.theta = self.theta - alpha * gradient
        return self.theta

    def fit(self, X, y, alpha=0.01, iterations=1000, lambda_=None):
        self.theta = np.zeros(X.shape[1])
        self.theta = self.gradient_descent(X, y, alpha, iterations, lambda_)

    def predict(self, X):
        return self.sigmoid(np.dot(X, self.theta))

    @staticmethod
    def sigmoid(z):
        return 1 / (1 + np.exp(-z))

    @staticmethod
    def h(X, theta):
        return LogisticRegression.sigmoid(np.dot(X, theta))


if __name__ == "__main__":
    np.random.seed(42)
    N = 11

    data = BreastCancerData(test_size=0.2, scale_data=True)
    logistic = LogisticRegression()

    result_matrix = np.zeros((N, N))
    for i, alpha in enumerate(np.linspace(0.001, 0.1, N)):
        for j, lambda_ in enumerate(np.linspace(0.001, 1, N)):
            logistic.fit(
                data.X_train,
                data.z_train,
                alpha=alpha,
                iterations=10_000,
                lambda_=lambda_,
            )
            a = logistic.predict(data.X_train) < 0.5
            b = data.z_train < 0.5
            score = np.mean(a == b)
            print(score, alpha, lambda_)
            result_matrix[i, j] = score

    print(result_matrix)
