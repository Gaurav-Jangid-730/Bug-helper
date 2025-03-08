
def log_vulnerability(target_dir, log):
    """Log findings to a file."""
    with open(f"{target_dir}/LOGS.txt", 'a') as f:
        f.write(f"\n{log}\n")

def ipv_46(target_dir,log):
    with open(f"{target_dir}/target_ips.txt","a") as f:
        f.write(f"\n{log}\n")