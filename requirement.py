# 将requirement.txt中的本地路径替换成版本号

import re
import subprocess

with open("requirements.txt", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "@" in line and "file://" in line:
        package_name = line.split("@")[0].strip()
        result = subprocess.run(["pip", "show", package_name], capture_output=True, text=True)
        version = re.search(r"Version:\s(.+)", result.stdout).group(1)
        new_lines.append(f"{package_name}=={version}\n")
    else:
        new_lines.append(line)

with open("requirements.txt", "w") as f:
    f.writelines(new_lines)
