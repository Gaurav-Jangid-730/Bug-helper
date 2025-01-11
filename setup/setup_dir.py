import os

def setup_directories(target):
    home_dir = os.path.expanduser("~")
    bug_dir = os.path.join(home_dir, "bug")
    target_dir = os.path.join(bug_dir,target)
    pay_dir = os.path.join(target_dir,"payloads")
    down_dir = os.path.join(target_dir,"downloads")
    screen_dir = os.path.join(target_dir,"screenshorts")
    interest_dir = os.path.join(target_dir,"interest")
    Dns_enum = os.path.join(target_dir,"DNS")
    ns_dir = os.path.join(Dns_enum,"NS")
    if not os.path.exists(bug_dir):
        os.makedirs(bug_dir)
        print(f"Created 'bug' folder at: {bug_dir}")
    else:
        print(f"'bug' folder already exists at: {bug_dir}")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        os.makedirs(pay_dir)
        os.makedirs(down_dir)
        os.makedirs(screen_dir)
        os.makedirs(interest_dir)
        os.makedirs(Dns_enum)
        os.makedirs(ns_dir)
        print(f"Created {target} folder at: {target_dir}")
    else:
        print(f"{target} folder already exists at: {target_dir}")
    return target_dir
