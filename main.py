from fastapi import FastAPI, Query
from typing import Optional
from datetime import datetime, timezone
import requests
from fastapi.responses import JSONResponse
 
 
app = FastAPI()
 
# For DEv
# WC_API_URL = "https://testingmarmorkrafts.store/wp-json/wc/v3"
# WC_CONSUMER_KEY = "ck_fb05462837d9679c0f6c8b11ccbac57d09c79638"
# WC_CONSUMER_SECRET = "cs_cd485ed45fc41da284d567e0d49cb8a272fbe4f1"
 
# For Prod
WC_API_URL = "https://marmorkrafts.com/wp-json/wc/v3"
WC_CONSUMER_KEY = "ck_fb05462837d9679c0f6c8b11ccbac57d09c79638"
WC_CONSUMER_SECRET = "cs_cd485ed45fc41da284d567e0d49cb8a272fbe4f1"

from fastapi import Query

@app.get("/blogs")
def get_blogs(keyword: str = Query(default=None, description="Search keyword for blog")):
    base_url = WC_API_URL.replace('/wc/v3', '')
    url = f"{base_url}/wp/v2/posts?per_page=5&_embed"

    # If a keyword is provided, add it to the search query
    if keyword:
        url += f"&search={keyword}"

    response = requests.get(url)

    if response.status_code != 200:
        return JSONResponse(
            status_code=response.status_code,
            content={"error": "Failed to fetch blog posts"}
        )

    posts = response.json()

    formatted = {
        "@context": "https://schema.org",
        "@type": "Collection",
        "name": "Blog Posts",
        "members": []
    }

    for post in posts:
        formatted["members"].append({
            "@type": "BlogPosting",
            "headline": post.get("title", {}).get("rendered", ""),
            "url": post.get("link"),
            "datePublished": post.get("date"),
            "author": {
                "@type": "Person",
                "name": post.get("_embedded", {}).get("author", [{}])[0].get("name", "Unknown")
            },
            "image": {
                "@type": "ImageObject",
                "url": post.get("_embedded", {}).get("wp:featuredmedia", [{}])[0].get("source_url", "")
            },
            "description": post.get("excerpt", {}).get("rendered", "")
        })

    return JSONResponse(content=formatted)

