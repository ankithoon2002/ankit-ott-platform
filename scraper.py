from bs4 import BeautifulSoup
import pandas as pd

print("🚀 Scraper Baba Active... Reading data locally from source.html...")

try:
    # 📁 Local HTML file ko open karna (Isme na internet chahiye na SSL check!)
    with open("source.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    all_movies = []

    # Page ke saare movie containers dhoondhna
    # WatchOMovies ke common card layouts check karna
    movie_items = soup.find_all('div', class_='movie-animated-item') or soup.find_all('article') or soup.find_all('div',
                                                                                                                  class_='gli')

    if not movie_items:
        # Agar upar waale tags na milein toh sabhi links wale wrapper dhoondhna
        movie_items = soup.find_all('div', class_='poster') or soup.find_all('div', class_='ml-item')

    print(f"📦 Total {len(movie_items)} posts detected in HTML. Starting extraction...")

    for item in movie_items:
        try:
            # 1. Title Extract Karna
            title_tag = item.find('h2') or item.find('a', class_='title') or item.find('img')
            if title_tag.name == 'img' and title_tag.has_attr('alt'):
                title = title_tag['alt'].strip()
            elif title_tag:
                title = title_tag.text.strip()
            else:
                title = "Unknown Title"

            # 2. Poster Link Extract Karna
            img_tag = item.find('img')
            if img_tag:
                poster_url = img_tag.get('src') or img_tag.get('data-original') or img_tag.get('data-src')
            else:
                poster_url = "https://ankit-ott-platform.onrender.com/static/default-poster.jpg"

            # 3. Platform Filter Engine (Ullu / MoodX)
            title_lower = title.lower()
            if 'moodx' in title_lower:
                platform = 'moodx'
            elif 'ullu' in title_lower:
                platform = 'ullu'
            else:
                platform = 'hot_series'

            # 4. Embedded Iframe Link Fallback (Kyunki hum offline hain, hum direct smart wrapper link laga denge)
            # Jab hum bulk import karenge toh yeh fallback link automatic video player chala dega
            server2_url = "https://streamoupload.xyz/embed-v75w1sesiokf.html"

            # Data collect karna
            if title != "Unknown Title":
                all_movies.append({
                    'title': title,
                    'category': 'hot_series',
                    'platform': platform,
                    'poster_url': poster_url,
                    'server2_url': server2_url
                })
                print(f"✅ Successfully Processed: {title} | Platform: {platform}")

        except Exception as e:
            continue

    # 🏁 AUTOMATIC EXCEL GENERATOR
    if all_movies:
        df = pd.DataFrame(all_movies)
        df.to_csv('movies_data.csv', index=False)
        print(
            "\n🎉 BOOM! JADOO HO GAYA! Saari bold movies ka data 'movies_data.csv' file me automatic save ho gaya hai!")
    else:
        print("⚠️ Code toh chal gaya par layout match nahi hua. Ek baar source.html check karo.")

except Exception as e:
    print(f"❌ Kuch gadbad hui: {e}")