import requests

def get_github():
    endpoint = "https://api.github.com"
    resp = requests.get(endpoint)
    print('resp_type', type(resp.json()))
    return resp.json()

if __name__=="__main__":
    print(get_github())
