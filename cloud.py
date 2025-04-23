import json
import jieba
from collections import Counter
from wordcloud import WordCloud
import numpy as np
from PIL import Image

# 1. 读取歌词数据
with open("lyrics.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# 2. 合并所有歌词
all_lyrics = "\n".join(song.get("lyrics", "") for song in data)

# 3. 中文分词处理
words = jieba.lcut(all_lyrics)

# 4. 扩展停用词列表
stopwords = set([
    "的", "了", "和", "是", "在", "我", "有", "也", "就", "都", "你", "他", "一个", "上", "这", "中", "对", "而", "到",
    "着", "那", "会", "着", "去", "来", "说", "它", "什么", "没有", "不是", "一个人", "怎么", "还是"
])

# 5. 过滤停用词和单字
filtered_words = [word for word in words if word not in stopwords and len(word) > 1]

# 6. 统计词频
word_counts = Counter(filtered_words)

# 7. 过滤掉低频词
min_frequency = 3  # 设置词频阈值，低于此值的词语将被过滤
filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_frequency}

# 8. 生成词频数据并关联歌曲
word_to_songs = {}
for song in data:
    song_title = song.get("title", "未知歌曲")
    song_lyrics = song.get("lyrics", "")
    for word in filtered_word_counts.keys():
        if word in song_lyrics:
            if word not in word_to_songs:
                word_to_songs[word] = []
            word_to_songs[word].append(song_title)

# 9. 构造前端需要的 JSON 数据
word_data = [
    {
        "keyword": word,
        "count": count,
        "songs": word_to_songs.get(word, [])
    }
    for word, count in sorted(filtered_word_counts.items(), key=lambda x: x[1], reverse=True)
]

# 10. 保存为 JSON 文件
with open("wordcount.json", "w", encoding="utf-8") as f:
    json.dump(word_data, f, ensure_ascii=False, indent=4)

print("词频统计已保存到 wordcount.json")

# 11. 处理轮廓图片
mask_image = Image.open("词云轮廓.png").convert("RGBA")
background = Image.new("RGBA", mask_image.size, (255, 255, 255, 255))
mask_image = Image.alpha_composite(background, mask_image).convert("L")
mask_array = np.where(np.array(mask_image) < 128, 0, 255).astype(np.uint8)

# 12. 自定义金色函数
def gold_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    base_lightness = 60  # 基础亮度（数值越大越接近浅黄）
    darkness = int((font_size / 150) * 30)  # 根据字号增加暗度
    return f"hsl(45, 75%, {max(25, base_lightness - darkness)}%)"  # 保持最低25%亮度

# 13. 生成词云
wordcloud = WordCloud(
    font_path="msyh.ttc",
    background_color=None,  # 设置背景为透明
    mode="RGBA",  # 支持透明背景
    mask=mask_array,
    max_words=1500,
    color_func=gold_color_func,  # 使用自定义颜色函数
    contour_width=0,
    repeat=True,
    prefer_horizontal=0.8,
    max_font_size=120,
    min_font_size=10,
    relative_scaling=0.4
).generate_from_frequencies(filtered_word_counts)

# 14. 保存词云图片
wordcloud.to_file("词云.png")  # 保存为支持透明背景的 PNG 文件

print("词云已生成：词云.png")