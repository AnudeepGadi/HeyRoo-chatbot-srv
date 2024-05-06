from client import QueryRpcClient

question = input("Enter your question: ")
query_rpc_client = QueryRpcClient()
answer = query_rpc_client.call(question) 
answer = answer.decode('utf-8')
print(answer)