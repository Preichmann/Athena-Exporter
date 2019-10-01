#!/usr/bin/python
import boto3
import json
import time
import schedule
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):

        print "Iniciando a query no athena..."
        
        client = boto3.client('athena', region_name='us-east-1')
        
        queryId = client.start_query_execution(
                QueryString='SELECT SUM(line_item_blended_cost) FROM default.awsbilling WHERE line_item_resource_id like \'%snap-%\' AND cast(month(current_date)AS DECIMAL) = cast(month AS DECIMAL) group by month order by month desc',
                ResultConfiguration={
                        'OutputLocation': 's3://aws-athena-query-results-701085748382-us-east-1/users/',
                        'EncryptionConfiguration': {
                    'EncryptionOption': 'SSE_S3'
                    }
                },
                WorkGroup='ANALYTICS_USERS'
        )["QueryExecutionId"]
        
        while(client.get_query_execution(QueryExecutionId=queryId)["QueryExecution"]["Status"]["State"] == 'RUNNING'):
            time.sleep(3)
        
        status = client.get_query_execution(QueryExecutionId=queryId)["QueryExecution"]["Status"]["State"]
        if(status != 'SUCCEEDED'):
                queryResult = status
        else:
          try:
            queryResult = client.get_query_results(
            QueryExecutionId=queryId
            )["ResultSet"]["Rows"][1]["Data"][0]["VarCharValue"]
          except IndexError as error:
            queryResult = 0

        g = GaugeMetricFamily("Costs", 'Help text', labels=['service'])
        g.add_metric(["Snapshots"], queryResult)
        yield g

if __name__ == '__main__':
    start_http_server(9103)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)