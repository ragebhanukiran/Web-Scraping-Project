# 📌 GitHub Topics Scraper

## 📖 Overview
This Python script scrapes GitHub topics and their top repositories using **BeautifulSoup** and **Requests**. It extracts information such as:
- Topic titles
- Descriptions
- URLs
- Top repositories (name, stars, owner, and repo link)
- Saves data as CSV files

## 🚀 Features
- Scrapes **GitHub Topics** dynamically
- Extracts **top repositories** for each topic
- Saves results in **CSV format**
- Handles **pagination and missing data gracefully**

## 🛠️ Tech Stack
- **Python** 🐍
- **BeautifulSoup** (for web scraping)
- **Requests** (for fetching web pages)
- **Pandas** (for data processing)

## 📦 Installation
### 1️⃣ Clone the Repository
```bash
https://github.com/ragebhanukiran/Web-Scraping-Project.git
cd github-topics-scraper
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 📊 How to Use
### Run the Script
```bash
python scraper.py
```
- This will scrape topics from GitHub and save data in the `data/` directory as CSV files.

## 📂 Output Structure
```
/github-topics-scraper
│── data/
│   ├── Machine Learning.csv
│   ├── Web Development.csv
│   ├── ...
│── scraper.py
│── requirements.txt
│── README.md
```

## 📝 Future Improvements
- Add **multithreading** for faster scraping
- Improve **error handling** and logging
- Implement a **GUI** for better user experience

---
✨ *Contributions are welcome! Feel free to fork and improve this scraper.* 🚀
