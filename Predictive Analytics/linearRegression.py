import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.tsa.deterministic import DeterministicProcess, CalendarFourier
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error, mean_squared_log_error,
    mean_absolute_percentage_error, median_absolute_error, max_error,
    explained_variance_score, mean_pinball_loss, d2_tweedie_score, d2_pinball_score
)

# Load and preprocess
df = pd.read_csv("train_cleansed.csv")
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True, errors='coerce')
df['month'] = df['Order Date'].dt.to_period('M')
monthly_sales = df.groupby('month')['Sales'].sum()
monthly_sales = pd.DataFrame(monthly_sales)
monthly_sales['time'] = np.arange(len(monthly_sales.index))

# Feature engineering for trend and seasonality
fourier = CalendarFourier(freq='ME', order=4)
dp = DeterministicProcess(
    index=monthly_sales.index,
    constant=True,
    order=2,
    additional_terms=[fourier],
    seasonal=True,
    drop=True
)
X = dp.in_sample()

# Train-test split
y = monthly_sales['Sales']
X_train = X.loc[:'2017-12']
X_test = X.loc['2018-01':]
y_train = y.loc[:'2017-12']
y_test = y.loc['2018-01':]

# Evaluation function
list_metrics = []
def evaluate_model(model_name, y_true, y_pred):
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    msle = mean_squared_log_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    medae = median_absolute_error(y_true, y_pred)
    me = max_error(y_true, y_pred)
    evs = explained_variance_score(y_true, y_pred)
    mpl = mean_pinball_loss(y_true, y_pred)
    d2t = d2_tweedie_score(y_true, y_pred)
    d2p = d2_pinball_score(y_true, y_pred)
    list_metrics.append([model_name, r2, mae, mse, msle, mape, medae, me, evs, mpl, d2t, d2p])
    print('{:^20} | {:^6} | {:^6} | {:^12} | {:^4} | {:^6} | {:^8} | {:^6} | {:^6} | {:^6} | {:^4} | {:^4} '.format(
         'Model','R2','MAE','MSE','MSLE','MAPE','MEDAE','ME','EVS','MPL','D2T','D2P'))
    formatl = ['{:<20} ','| {:^6.2f} ','| {:^6.0f} ','| {:^12,.0f}',' | {:^4.2f}',' | {:^6.2f}',' | {:^8.0f}',' | {:^6.0f}',' | {:^6.2f}',' | {:^6.0f}',
          ' | {:^4.2f} |',' {:^4.2f} ']
    for metrics in list_metrics:
        for format_, value in zip(formatl, metrics):
            print(format_.format(value), end="")
        print()

# -----------------------------
# Linear Regression Model
# -----------------------------
print("Linear Regression results:")
model_lr = LinearRegression(fit_intercept=False)
model_lr.fit(X_train, y_train)
y_pred1_lr = pd.Series(model_lr.predict(X_train), index=X_train.index)
y_pred2_lr = pd.Series(model_lr.predict(X_test), index=X_test.index)
y_forecast_lr = pd.Series(model_lr.predict(dp.out_of_sample(steps=12)), index=dp.out_of_sample(steps=12).index)

print('R² train:', r2_score(y_train, y_pred1_lr))
print('R² test:', r2_score(y_test, y_pred2_lr))
evaluate_model("LinearReg", y_test, y_pred2_lr)

ax = monthly_sales['Sales'].plot(style="-.", color="0.5", title="Forecast Using Linear Regression - Including Trend and Seasonality")
y_pred1_lr.plot(ax=ax, linewidth=3, label="Trend (Train)")
y_pred2_lr.plot(ax=ax, linewidth=3, label="Trend (Test)")
y_forecast_lr.plot(ax=ax, linewidth=3, label="Trend Forecast", color='C3')
plt.legend()
plt.show()

# -----------------------------
# AdaBoost Regression Model
# -----------------------------
print("\nAdaBoost Regression results:")
model_ada = AdaBoostRegressor(
    n_estimators=40,
    estimator=LinearRegression(),
    loss='square',
    learning_rate=0.5,
    random_state=21
)
model_ada.fit(X_train, y_train)

y_pred1_ada = pd.Series(model_ada.predict(X_train), index=X_train.index)
y_pred2_ada = pd.Series(model_ada.predict(X_test), index=X_test.index)
y_forecast_ada = pd.Series(model_ada.predict(dp.out_of_sample(steps=12)), index=dp.out_of_sample(steps=12).index)

print('R² train:', r2_score(y_train, y_pred1_ada))
print('R² test:', r2_score(y_test, y_pred2_ada))
evaluate_model("AdaBoost", y_test, y_pred2_ada)

ax = monthly_sales['Sales'].plot(style="-.", color="0.5", title="Forecast - with AdaBoost")
y_pred1_ada.plot(ax=ax, linewidth=3, label="AdaBoost (Train)")
y_pred2_ada.plot(ax=ax, linewidth=3, label="AdaBoost (Test)", color='C2')
y_forecast_ada.plot(ax=ax, linewidth=3, label="AdaBoost Forecast", color='C3')
plt.legend()
plt.show()
