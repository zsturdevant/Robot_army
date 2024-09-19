import requests

# record the time needed to recieve a response
def response_time(url):
    result = requests.get(url)
    return result.elapsed.total_seconds()

## sends a request to the target 10 times and records the
## average response time for comparison
if __name__ == '__main__':

    url = "http://137.165.8.200/" 
    times = []
    for _ in range(0,10):
        times.append(response_time(url))

    average = 0
    for tim in times:
        print(tim)
        average += tim
        
    average = average / 10
    print(average)
