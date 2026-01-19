# Thor Data Web Unlocker Documentation

> Source: [Thor Data Docs - Web Unlocker](https://doc.thordata.com/doc/scraping/web-unlocker)

## Overview

Web Unlocker efficiently bypasses anti-scraping mechanisms by simulating real user behavior and intelligently handling complex processes such as proxy management, fingerprint analysis, and CAPTCHA resolution. It can automatically overcome access restrictions and retrieve target webpage data in **HTML** or **PNG** format in a reliable manner.

Web Unlocker simplifies the data collection process by providing clear response results with a single request, eliminating the need for managing proxies or anti-scraping strategies. This allows users to focus on their core business operations.

---

## Common Use Cases

- **Advertising Alliance:** Ensures precise targeting, improves conversion rates and revenue, and helps maximize the earnings of content creators.
- **Social Media:** Intelligently scrape social content to enhance market insight. Easily unlock social platform data.
- **Market Analysis:** Monitor brand data, scrape websites required by the industry, and analyze market trends.
- **Brand Monitoring:** Track brand keywords and automatically retrieve user reviews and other data for research purposes.

---

## Quick Start Guide

### How to Start Using the Web Unlocker

Follow these simple steps to quickly start using Thordata's API to bypass website restrictions and seamlessly extract data:

1. **Register:** Visit the [Thordata official website](https://dashboard.thordata.com/login), click [Register](https://dashboard.thordata.com/register) and fill in your email address, password, and other details to complete the registration. Alternatively, register instantly using your Google or GitHub account.

2. **Apply for a Free Trial:** After logging in, navigate to **Web Unlocker > Pricing** to apply for a free trial.

3. **Obtain Your API Token:** After claiming your free trial, go to **API Playground > "Token"** to copy your token.

4. **Configure Parameters:** After selecting your target URL, you can configure core parameters and output formats including JavaScript rendering, country/region targeting, and HTML/PNG outputs.

5. **Start Scraping:** After configuring the parameters, click on **Start Scraping** to view the real-time captured results (PNG/HTML).

6. **Preview and Download Results:** After the task is completed, the right-side panel will display the final scraped data based on the selected output type, along with options to download the PNG or HTML source code.

---

## Send Your First Request

Before you start, you will need an **API Token**.

1. Get a free trial on the [Pricing page](https://dashboard.thordata.com/universal-scraping).
2. Copy your credentials under **API Playground > "Token"**.

### Code Examples

#### cURL

```bash
curl -X POST https://webunlocker.thordata.com/request \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "url=https://www.google.com" \
  -d "type=html" \
  -d "js_render=True" \
  -d "header=False"
```

#### Python

```python
import http.client
from urllib.parse import urlencode

conn = http.client.HTTPSConnection("universalapi.thordata.com")

payload = {
    "url": "https://www.google.com",
    "type": "html",
    "js_render": "True",
    "header": "False"
}

form_data = urlencode(payload)

headers = {
    'Authorization': "Bearer token",
    'content-type': "application/x-www-form-urlencoded"
}

conn.request("POST", "/request", form_data, headers)

res = conn.getresponse()
data = res.read()

print(f"Status: {res.status} {res.reason}")
print(data.decode("utf-8"))
```

#### Node.js

```javascript
const https = require("https");
const querystring = require("querystring");

const options = {
  method: "POST",
  hostname: "universalapi.thordata.com",
  path: "/request",
  headers: {
    "Authorization": "Bearer token",
    "content-type": "application/x-www-form-urlencoded"
  }
};

const formData = {
  url: "https://www.google.com",
  type: "html",
  js_render: "True",
  header: "False"
};

const formDataString = querystring.stringify(formData);
options.headers["Content-Length"] = formDataString.length;

const req = https.request(options, (res) => {
  const chunks = [];
  res.on("data", (chunk) => chunks.push(chunk));
  res.on("end", () => {
    const body = Buffer.concat(chunks);
    console.log(body.toString());
  });
});

req.write(formDataString);
req.end();
```

#### Go

```go
package main

import (
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
    "net/url"
    "strings"
    "time"
)

func main() {
    var apiKey = "token"
    var targetURL = "https://universalapi.thordata.com/request"

    formData := url.Values{
        "url":       {"https://www.google.com"},
        "type":      {"html"},
        "js_render": {"True"},
        "header":    {"False"},
    }

    client := &http.Client{Timeout: 30 * time.Second}
    req, err := http.NewRequest("POST", targetURL, strings.NewReader(formData.Encode()))
    if err != nil {
        log.Fatal("Create request failed:", err)
    }

    req.Header = http.Header{
        "Authorization": {"Bearer " + apiKey},
        "Content-Type":  {"application/x-www-form-urlencoded"},
    }

    res, err := client.Do(req)
    if err != nil {
        log.Fatal("Failed to send request:", err)
    }
    defer res.Body.Close()

    body, err := ioutil.ReadAll(res.Body)
    if err != nil {
        log.Fatal("Failed to read response:", err)
    }

    fmt.Printf("Status: %d Content:%s", res.StatusCode, body)
}
```

---

## Response Format

After sending the request, it will return output results in **HTML format**:

```html
<!DOCTYPE html>
<html itemscope="" itemtype="http://schema.org/WebPage" lang="en">
<head>
  <meta charset="UTF-8">
  <meta content="origin" name="referrer">
  <!-- ... page content ... -->
</head>
<body>
  <!-- ... -->
</body>
</html>
```

---

## Need Help?

For further assistance, please contact Thor Data at:

- **Email:** support@thordata.com
