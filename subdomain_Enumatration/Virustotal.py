import requests
import json

def get_subdomains(domain, api_key):
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        subdomains = data.get("data", {}).get("attributes", {}).get("subdomains", [])
        
        if subdomains:
            filename = f"{domain}_subdomains.txt"
            with open(filename, "w") as file:
                for subdomain in subdomains:
                    file.write(subdomain + "\n")
            print(f"Subdomains saved to {filename}")
        else:
            print("No subdomains found.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Example usage:
# Replace 'your_api_key_here' with your actual VirusTotal API key
#get_subdomains("google.com", "your_api_key_here")
