import requests

def get_subdomains(target_dir,domain, api_key):
    filename = f"{target_dir}/{domain}_subdomains.txt"
    BASE_URL = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains?limit=40"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key
    }

    subdomains = []
    cursor = None

    while True:
        url = BASE_URL
        if cursor:
            url = cursor
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Error:", response.json())
            break

        data = response.json()
        
        # Extract subdomains
        for entry in data.get("data", []):
            subdomains.append(entry.get("id"))

        # Get next cursor if available
        cursor = data.get("links",{}).get("next")
        if not cursor:
            break
    with open(filename, "w") as file:
        for subdomain in subdomains:
            file.write(subdomain + "\n")
    print(f"Subdomains saved to {filename}")
