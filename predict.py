from utils import run_query
from math import sqrt
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error


def conv_to_df(records_dict_list):
    cols = records_dict_list[0].keys()
    records_dict = {}
    for col in cols:
        records_dict[col] = [record[col] for record in records_dict_list]
    return pd.DataFrame(records_dict)


def preprocess_data(records_df):
    idx = records_df.groupby(['ConsumerID'])['DateOfPurchase'].transform(min) == records_df[
        'DateOfPurchase']
    filtered_df = records_df[idx][['DateOfPurchase']]
    filtered_df['Count'] = 1
    filtered_df = filtered_df.groupby(['DateOfPurchase']).sum()

    # we will be dropping the last date 25-02-2018 because the count for this date may not be complete.
    filtered_df = filtered_df.drop(filtered_df.index[-1])

    filtered_df.index = pd.to_datetime(filtered_df.index)
    return filtered_df


def predict_consumers():
    consumer_product_records = run_query("select ConsumerProductID, ConsumerID, DateOfPurchase from consumer_product")
    consumer_product_df = conv_to_df(consumer_product_records)
    filtered_df = preprocess_data(consumer_product_df)

    # Dividing Train - Test data set taking all days of March, April and May 2018 as test data and rest as train data
    train = filtered_df.loc[:'2018-02-28']
    test = filtered_df.loc['2018-03-01':]

    y_hat_avg = test.copy()
    fit1 = sm.tsa.statespace.SARIMAX(train.Count, order=(2, 1, 4), seasonal_order=(0, 1, 1, 7)).fit()
    y_hat_avg['SARIMA'] = fit1.predict(start="2018-03-01", end="2018-05-24", dynamic=True)
    y_hat_avg['SARIMA'] = fit1.forecast(len(test))

    rms = sqrt(mean_squared_error(test.Count, y_hat_avg.Holt_Winter))
    print("RMSE is {}".format(rms))

    predicted_daily = fit1.predict(start="2018-06-01", end="2018-08-31", dynamic=True)
    predicted_monthly = predicted_daily.resample('m').sum()
    print("Predicted Number of Consumers in June 2018 = {}".format(int(predicted_monthly.loc['2018-06'])))
    print("Predicted Number of Consumers in July 2018 = {}".format(int(predicted_monthly.loc['2018-07'])))
    print("Predicted Number of Consumers in August 2018 = {}".format(int(predicted_monthly.loc['2018-08'])))
