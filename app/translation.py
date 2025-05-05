import aiohttp
import os


async def translate_text(text: str, source_lang: str = "ru", target_lang: str = "en") -> str:
    if not text:
        return ""

    url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"

    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "deep-translate1.p.rapidapi.com"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["data"]["translations"]["translatedText"][0]
                else:
                    error_text = await response.text()
                    print(f"Translation error: {error_text}")
                    return f"Translation error: {response.status}"
    except Exception as e:
        print(f"Translation request failed: {str(e)}")
        return f"Translation failed: {str(e)}"
