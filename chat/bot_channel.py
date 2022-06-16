from pyspark.sql import *
from pyspark.sql.functions import *


def main():

  spark = SparkSession \
      .builder \
      .appName("chat_client") \
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

  result = words.writeStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("topic", "chat_chanel_ban").option("checkpointLocation", "home/tanguy/Bureau/spark/chat").start()
  result.awaitTermination()

if __name__ == "__main__":
    try:
        main()
    except Exception as error_exception:
        print("ERROR: %s" % error_exception)