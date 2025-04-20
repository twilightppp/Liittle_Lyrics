import requests
from bs4 import BeautifulSoup
import json
import re

# 网易云音乐专辑页面 URL 模板
BASE_URL = "https://music.163.com/album?id={}"

# 专辑 ID 对应的专辑名
ALBUMS = {
    "39483040": "平凡的一天",  
    "83823905": "小王",        
    "127551538": "幼鸟指南",        
    "244922245": "冒险精神"     
}

# 网易云音乐歌词 API 模板
LYRICS_API = "https://music.163.com/api/song/lyric?id={}&lv=1&kv=1&tv=-1"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://music.163.com/"
}

# 存储结果的列表
lyrics_data = []

def get_album_songs(album_id, album_name):
    """获取专辑中的所有歌曲"""
    url = BASE_URL.format(album_id)
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # 网易云音乐的 iframe 中的歌曲列表
    song_list = soup.find("ul", class_="f-hide").find_all("a")
    for song in song_list:
        song_name = song.text.strip()
        song_id = re.search(r"id=(\d+)", song["href"]).group(1)
        print(f"正在爬取歌曲: {song_name} ({song_id})")
        get_song_lyrics(song_id, song_name, album_name)

def get_song_lyrics(song_id, song_name, album_name):
    """获取歌曲的歌词"""
    url = LYRICS_API.format(song_id)
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    if "lrc" in data and "lyric" in data["lrc"]:
        raw_lyrics = data["lrc"]["lyric"]
        # 去掉时间戳
        lyrics = re.sub(r"\[.*?\]", "", raw_lyrics).strip()
        lyrics_data.append({
            "title": song_name,
            "lyrics": lyrics
        })
    else:
        print(f"未找到歌词: {song_name}")

def save_to_json():
    """保存结果到 lyrics.json"""
    with open("lyrics.json", "w", encoding="utf-8") as f:
        json.dump(lyrics_data, f, ensure_ascii=False, indent=4)
    print("歌词已保存到 lyrics.json")

def main():
    for album_id, album_name in ALBUMS.items():
        print(f"正在爬取专辑: {album_name}")
        get_album_songs(album_id, album_name)
    save_to_json()

if __name__ == "__main__":
    main()