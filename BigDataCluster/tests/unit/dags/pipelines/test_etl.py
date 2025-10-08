import unittest
from pyspark.sql import SparkSession
from dags.pipelines.etl import ETL


class TestETL(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("unit_test").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_validate_fields(self):
        # Sample data
        data = [(None, 19), ("name", None), ("", 23), ("name", 25)]
        columns = ["name", "age"]
        df = self.spark.createDataFrame(data, columns)

        validations = [
            {
                "field": "age",
                "validations": ["notNull"]
            },
            {
                "field": "name",
                "validations": ["notEmpty", "notNull"]
            }
        ]

        etl = ETL(self.spark, None, None, None, None)
        result = etl.validate_fields(df, validations)

        # Check valid rows
        ok_df = result['ok']
        self.assertEqual(ok_df.count(), 1)

        # Check invalid rows
        ko_df = result['ko']
        self.assertEqual(ko_df.count(), 3)

    def test_add_fields(self):
        # Sample data
        data = [("name", 25)]
        columns = ["name", "age"]
        df = self.spark.createDataFrame(data, columns)

        fields = [
            {
                "name": "dt",
                "function": "current_timestamp"
            }
        ]

        etl = ETL(self.spark, None, None, None, None)
        result_df = etl.add_fields(df, fields)

        # Check if the field has been added
        self.assertTrue("dt" in result_df.columns)
