from pyspark.sql import *
from pyspark.sql.functions import *


def main():

  spark = SparkSession \
      .builder \
      .appName("chat_client") \
      .config("failOnDataLoss", "false") \
      .config('spark.executor.instances', 4) \
      .config('spark.executor.cores', 4) \
      .config('spark.executor.memory', '10g')\
      .config('spark.driver.memory', '15g')\
      .config('spark.memory.offHeap.enabled', True)\
      .config('spark.memory.offHeap.size', '20g')\
      .config('spark.dirver.maxResultSize', '4096') \
      .getOrCreate()


  df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "chat_channel_bot") \
    .load()

  words = df.select(
   explode(split(df.value, " ")).alias("value")
)

  result = words.writeStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("topic", "chat_chanel_consumer").option("checkpointLocation", "home/tanguy/Bureau/spark/chat").start()
  result.awaitTermination()

if __name__ == "__main__":
    try:
        main()
    except Exception as error_exception:
        print("ERROR: %s" % error_exception)