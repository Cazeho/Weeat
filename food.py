
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Optional

app = FastAPI()

def scrape_food_trucks(url: str, target_day: str, target_week: str) -> List[Dict]:
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    foodtrucks_data = []

    for calendar_div in soup.find_all('div', class_='calendar-slot hidden'):
        data_week = calendar_div.get('data-week')
        data_day = calendar_div.get('data-day')
        
        if data_day == target_day and data_week == target_week:
            for foodtruck_div in calendar_div.find_all('div', class_='foodtruck-infos'):
                title_tag = foodtruck_div.find('h3', class_='foodtruck-title')
                if not title_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                
                # Find the corresponding image
                img_div = foodtruck_div.find_previous('div', class_='c-article-box__img')
                img = img_div.find('img') if img_div else None
                img_src = img.get('src') if img else None
                
                foodtrucks_data.append({
                    'name': title,
                    'image': img_src,
                    'day': data_day,
                    'week': data_week
                })
        elif  target_day == None and target_week == None :
            if data_week and data_day:
                for foodtruck_div in calendar_div.find_all('div', class_='foodtruck-infos'):
                    title_tag = foodtruck_div.find('h3', class_='foodtruck-title')
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    
                    # Find the corresponding image
                    img_div = foodtruck_div.find_previous('div', class_='c-article-box__img')
                    img = img_div.find('img') if img_div else None
                    img_src = img.get('src') if img else None
                    
                    foodtrucks_data.append({
                        'name': title,
                        'image': img_src,
                        'day': data_day,
                        'week': data_week
                    })
    
    return foodtrucks_data

@app.get("/food-trucks", response_model=List[Dict])
def get_food_trucks(day: Optional[str] = Query(None), week: Optional[str] = Query(None)):
    url = "https://parisladefense.com/fr/decouvrir/food-trucks"
    data = scrape_food_trucks(url, day, week)
    if data:
        return data
    else:
        return {"message": "No data found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
