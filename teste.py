#!/usr/bin/python
import boto3
import json
import SimpleHTTPServer
import SocketServer
 
PORT = 8201

client = boto3.client('athena')

queryId = client.start_query_execution(
	QueryString='SELECT SUM(line_item_blended_cost) FROM awsbilling WHERE line_item_resource_id like \'%snap-%\' AND cast(month(current_date)AS DECIMAL) = cast(month AS DECIMAL) group by month order by month desc;',
	QueryExecutionContext={
		'Database': 'default'
	},
	WorkGroup='ANALYTICS_USERS'
)["QueryExecutionId"]

while(client.get_query_execution(QueryExecutionId=queryId) == 'RUNNING'):
	time.sleep(1)
	print "durmiu 1s"
else:
	status = client.get_query_execution(QueryExecutionId=queryId)["QueryExecution"]["Status"]["State"]
	if(status != 'SUCCEEDED'):
		queryResult = status
	else:
		queryResult = client.get_query_results(
			QueryExecutionId=queryId
		)["ResultSet"]["Rows"][1]["Data"][0]["VarCharValue"]


class my_handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
   def do_GET(self):
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write("<a>"+queryResult+"</a>")
      return
 
 
try:
   httpd = SocketServer.ThreadingTCPServer(('', PORT), my_handler)
 
   print "servidor web rodando na porta ", PORT
   httpd.serve_forever()
 
except KeyboardInterrupt:
   print "Voce pressionou ^C, encerrando..."
   httpd.socket.close()