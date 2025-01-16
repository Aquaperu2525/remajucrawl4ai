import asyncio
import nest_asyncio
from crawl4ai import AsyncWebCrawler,CacheMode, BrowserConfig, CrawlerRunConfig # type: ignore
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
import base64
import json
from PIL import Image
from io import BytesIO
import os
import math
from collections import Counter
import re
from pydantic import BaseModel, Field
nest_asyncio.apply()
import time

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='confactura-remaju.json'
WORD = re.compile(r"\w+")

def base64_to_image(base64_string):
  # Remove the data URI prefix if present
  if "data:image" in base64_string:
      base64_string = base64_string.split(",")[1]
      print(base64_string)

  # Decode the Base64 string into bytes
  image_bytes = base64.b64decode(base64_string)
  return image_bytes

def create_image_from_bytes(image_bytes):
  # Create a BytesIO object to handle the image data
  image_stream = BytesIO(image_bytes)

  # Open the image using Pillow (PIL)
  image = Image.open(image_stream)
  return image

def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    # for non-dense text 
    # response = client.text_detection(image=image)
    # for dense text
    response = client.text_detection(image=image)
    texts = response.text_annotations
    #print(texts)
    ocr_text = ""

    for text in texts:
        ocr_text = text.description

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    
    return ocr_text

        

async def main():
    # Initialize browser config
    browser_config = BrowserConfig(
        headless=True
    )

    # Initialize crawler config with JavaScript code to click "Load More"
    js_code = [
        "document.querySelector('.ui-corner-left').click(); document.querySelector('.captcha-input').value='J1569'; document.querySelector('.ui-password').value='Messenger2'; document.querySelector('.ui-inputtext').value='191543';document.querySelector('.btn-rojo').click();"
    ]

    session_id = "typescript_commits_session"
    schema = {
            "name": "Commit Extractor",
            "baseSelector": ".ui-inputgroup",
            "fields": [
                {
                    "name": "src",
                    "selector": ".captcha-img-fix",
                    "type": "attribute",
                    "attribute":"src"
                    
                },
            ],
        }
    extraction_strategy = JsonCssExtractionStrategy(schema)
    

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        #session_id=session_id,
        #css_selector="captcha-img-fix",
        #extraction_strategy=extraction_strategy,
        css_selector="li.Box-sc-g0xbh4-0 h4.markdown-title",

    )
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            #url="https://remaju.pj.gob.pe/remaju/pages/seguridad/login.xhtml",
            url="https://github.com/microsoft/TypeScript/commits/main",
            config=crawler_config
        )
        
        assert result.success, "Failed to crawl the page"
        print(result.markdown)
        #news_teasers = json.loads(result.extracted_content)
        #print(f"Successfully extracted {len(news_teasers)} news teasers")
        #imagen64 = news_teasers[0]
        #print(imagen64)
        #image_bytes = base64_to_image(imagen64['src'])

        # Create an image from bytes
        #img = create_image_from_bytes(image_bytes)

        # Display or save the image as needed
        #img.show()
        #img.save("output_image.jpg")
        #time.sleep(2)
        #print(detect_text('/workspaces/codespaces-blank/output_image.jpg'))

if __name__ == "__main__":
    asyncio.run(main())
 


