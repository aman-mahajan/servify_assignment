
from utils import run_query
import matplotlib.dates as dates
from collections import Counter
from predict import predict_consumers

nonelist = [[], {}, None, 'none', 'None', 'null', 'Null', 'NULL', (), '']


def get_average_plans_sold_per_week():
    records = run_query("select SoldPlanID, DateOfPurchase from sold_plan")
    start_date = min([record['DateOfPurchase'] for record in records])
    end_date = max([record['DateOfPurchase'] for record in records])

    start_date_num = dates.datestr2num(start_date.strftime('%Y%m%d'))
    end_date_num = dates.datestr2num(end_date.strftime('%Y%m%d'))

    date_range = [x for x in range(int(start_date_num), int(end_date_num + 1))]

    daily_plan_sold_array = [0] * len(date_range)
    for record in records:
        date = record.get('DateOfPurchase')
        idx = int(dates.datestr2num(date.strftime('%Y%m%d'))) - int(start_date_num)
        daily_plan_sold_array[idx] += 1

    total_plans_sold = len(records)
    total_days = len(date_range)
    total_weeks = total_days / 7
    average_plans_sold_per_week = total_plans_sold / total_weeks
    return average_plans_sold_per_week


def get_top_k_brands_sold(k):
    if k in nonelist or k < 1:
        return []
    records = run_query("SELECT sold_plan.SoldPlanID, consumer_product.BrandID FROM sold_plan INNER JOIN "
                        "consumer_product ON sold_plan.ConsumerProductID=consumer_product.ConsumerProductID")
    brandid_sold_array = [record['BrandID'] for record in records]
    k_most_common = Counter(brandid_sold_array).most_common(k)
    return [{'BrandID': brand, 'Count': count} for brand, count in k_most_common]


def get_fraction():
    query = "SELECT a.on_plan_count/b.total_request FROM " \
            "(SELECT COUNT(*) AS on_plan_count FROM consumer_servicerequest WHERE SoldPlanID != 0) a, " \
            "(SELECT COUNT(*) AS total_request FROM consumer_servicerequest) b"
    result = run_query(query)
    return result


def process_all():
    average_plans_sold_weekly = get_average_plans_sold_per_week()
    print("Average plans Sold Weekly= {}".format(average_plans_sold_weekly))

    top_5_brands = get_top_k_brands_sold(5)
    if top_5_brands in nonelist:
        print("Incorrect input k")
    print("Top 5 brands with their count are:")
    for brand in top_5_brands:
        print("BrandID: {}  has {} plans sold against it.".format(brand['BrandID'], brand['Count']))

    result = get_fraction()
    print("{}".format(result))

    predict_consumers()


if __name__ == '__main__':
    process_all()
