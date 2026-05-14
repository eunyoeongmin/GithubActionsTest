import os

status = "Success"
message = "修正確認"

html_content = f"""<!DOCTYPE html>
<html lang="en">
<html>
<head><title>ci/cd test</title></head>
<body style="font-family: sans-serif: text-alingn: center; padding-top: 50px;">
    <h1> CI/CD Test Report</h1>
    <p style="font-size: 20px;">Status: <strong>{status}</strong></p>
    <p>{message}</p>
    <hr>
    <p>last updated: {os.popen('date').read()}</p>
</body>
</html>"""

os.makedirs("public", exist_ok=True)
with open("public/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)