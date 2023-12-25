import json
from datetime import datetime
from pyspark.sql import SparkSession

spark=SparkSession.builder.appName('Spark_lab5').config("spark.some.config.option").getOrCreate()
sc=spark.sparkContext
data_file="rides.txt"
rdd=sc.textFile(data_file, minPartitions=100).map(lambda x: eval(x))

feedback_categories = ['politeness', 'car', 'navigation']
def count_negative_feedback(trip):
    feedback = trip['driver_feedback']
    counts = [0, 0, 0]
    for i, category_feedback in enumerate(feedback):
        if category_feedback == -1:
            counts[i] += 1
    return list(zip(feedback_categories, counts))

# Обчислення найбільш скаржених категорій
negative_feedback_counts = rdd.flatMap(count_negative_feedback) \
    .reduceByKey(lambda a, b: a + b) \
    .collect()

# Сортування та виведення результату
sorted_feedback = sorted(negative_feedback_counts, key=lambda x: -x[1])
print(sorted_feedback)

with open("sorted_feedback.json", "w") as f:
   json.dump(sorted_feedback,f,indent=4,sort_keys=True)

