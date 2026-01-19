# Thor Data Residential Proxies Documentation

> Source: [Thor Data Docs - Residential Proxies](https://doc.thordata.com/doc/proxies/residential-proxies)

## Overview

Residential Proxies use authentic ISP-allocated (Internet Service Providers) IPs from real user devices, not data centers, bypassing detectable data center infrastructures. This residential network architecture achieves superior anonymity and can reduce blocking risks. Ideal for accessing geographically restricted content and conducting large-scale web scraping without detection.

---

## Getting Started

Thordata provides a comprehensive Dynamic Residential Proxy Service, covering over **195 countries** with access to more than **60 million legitimate residential IPs**. These IPs, originating from real residential networks, overcome geographical restrictions.

### Service Features

- **Intelligent IP Rotation**
- **Country/City/ASN-Level Targeting**
- **Millisecond Response Times** (<0.5s)
- **99.82% Connection Success Rate**
- **Exceptional Download Speeds & Persistent Connection Stability**

### Ideal Use Cases

- ✅ Large-Scale Web Scraping & Search
- ✅ Cross-Border Market Monitoring & Competitive Intelligence
- ✅ Brand Protection & Infringement Monitoring
- ✅ Automated Public Data Collection & Aggregation

### Authentication Methods

Dynamic Residential Proxies support two authentication methods:
1. **User & Pass auth**
2. **Whitelisted IPs**

---

## Making Requests

### Basic Queries

Execute requests with only `USERNAME` and `PASSWORD`. Uses random residential IPs that rotate with each request. Every new request will use a different proxy.

#### cURL Example

```bash
curl -x "https://td-customer-USERNAME:PASSWORD@t.pr.thordata.net:9999" "https://ipinfo.thordata.com"
```

#### Python Example

```python
import requests

username = "td-customer-USERNAME"
password = "PASSWORD"
proxy_server = "t.pr.thordata.net:9999"

proxies = {"https": f"https://{username}:{password}@{proxy_server}"}

response = requests.get("https://ipinfo.thordata.com", proxies=proxies)
print(response.text)
```

#### Node.js Example

```javascript
const rp = require('request-promise');

const username = "td-customer-USERNAME";
const password = "PASSWORD";
const proxyServer = "t.pr.thordata.net:9999";

rp({
  url: 'https://ipinfo.thordata.com',
  proxy: `https://${username}:${password}@${proxyServer}`,
})
  .then(function(data) {
    console.log(data);
  })
  .catch(function(err) {
    console.error(err);
  });
```

---

### Targeted Requests

Thordata allows embedding geo-targeting and session parameters directly in your username to specify proxy locations (Continent/Country/State/City) or control Session.

#### Example: Using a proxy from Melbourne, Australia with a 10-minute sticky session

```bash
curl -x "https://td-customer-USERNAME-country-au-state-victoria-city-melbourne-sessid-au123-sesstime-10:PASSWORD@t.pr.thordata.net:9999" "https://ipinfo.thordata.com"
```

---

## Request Parameters

| Parameter   | Description                                      | Example                 |
|-------------|--------------------------------------------------|-------------------------|
| `username`  | Proxy account credential                         | `td-customer-username`  |
| `continent` | Target continent (omit for random)               | `continent-asia`        |
| `country`   | Two-letter country code (omit for random)        | `country-au`            |
| `state`     | Target state (omit for random)                   | `state-victoria`        |
| `city`      | Target city (can be set without `state`)         | `city-melbourne`        |
| `session`   | Required for Sticky IP and switching IPs         | `sessid-au123456`       |
| `sessTime`  | IP duration (1-90 minutes)                       | `sesstime-10`           |
| `password`  | Proxy account password                           | `password`              |
| `asn`       | Specific ISP (omit for random)                   | `asn-AS1221`            |

---

## Need Help?

For further clarification or help with location targeting, please contact Thor Data via:

- **Email:** support@thordata.com
- **Live Chat:** 24/7 available on [thordata.com](https://www.thordata.com/)
