"""
AI Analyzer Module - Uses Google Gemini API (FREE) for news analysis and predictions
"""
import google.generativeai as genai
from datetime import datetime
from typing import List, Dict, Optional
import logging
import json

from config import config
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        # Sử dụng Gemini 1.5 Flash - nhanh và miễn phí
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _format_articles_for_prompt(self, articles: List[Dict]) -> str:
        """Format articles into a structured text for the prompt"""
        if not articles:
            return "Không có tin tức mới trong 24 giờ qua."
        
        formatted = []
        for i, article in enumerate(articles[:30], 1):  # Limit to 30 articles
            formatted.append(f"""
{i}. [{article['source']} - {article['region']}]
   Tiêu đề: {article['title']}
   Tóm tắt: {article.get('summary', 'N/A')[:200]}
   Thời gian: {article.get('published_date', 'N/A')}
""")
        return "\n".join(formatted)
    
    def analyze_news(self, articles: List[Dict]) -> Dict:
        """
        Analyze news articles and generate predictions
        Returns structured analysis with political summary and financial predictions
        """
        today = datetime.now().strftime("%Y-%m-%d")
        articles_text = self._format_articles_for_prompt(articles)
        
        prompt = f"""Bạn là một chuyên gia phân tích chính trị và tài chính quốc tế. 
Hôm nay là {today}. Dựa trên các tin tức được thu thập trong 24 giờ qua, hãy phân tích và đưa ra dự đoán.

=== TIN TỨC THU THẬP ĐƯỢC ===
{articles_text}

=== YÊU CẦU PHÂN TÍCH ===

Hãy viết một báo cáo phân tích bằng tiếng Việt với cấu trúc sau:

## 📰 TỔNG HỢP TIN TỨC CHÍNH TRỊ

### 🇺🇸 Hoa Kỳ
[Tóm tắt các tin quan trọng về Mỹ, chính sách, động thái của chính quyền]

### 🇨🇳 Trung Quốc  
[Tóm tắt các tin về Trung Quốc, quan hệ quốc tế, chính sách]

### 🇷🇺 Nga
[Tóm tắt các tin về Nga, xung đột Ukraine, quan hệ quốc tế]

### 🇯🇵 Nhật Bản
[Tóm tắt các tin về Nhật Bản, chính sách kinh tế, an ninh khu vực]

### 🌏 Điểm nóng khác
[Các tin quan trọng khác ảnh hưởng đến địa chính trị]

---

## 📊 DỰ ĐOÁN TÀI CHÍNH (7-14 ngày tới)

### 🛢️ Giá dầu
- Xu hướng: [Tăng/Giảm/Đi ngang]
- Lý do: [Giải thích dựa trên tin tức chính trị]
- Mức dự đoán: [Nếu có thể ước tính]

### 🥇 Giá vàng
- Xu hướng: [Tăng/Giảm/Đi ngang]
- Lý do: [Giải thích - thường liên quan đến căng thẳng địa chính trị, lạm phát]

### 🏠 Thị trường bất động sản (xu hướng chung)
- Nhận định: [Dựa trên chính sách tiền tệ, kinh tế vĩ mô]

### 📈 Thị trường chứng khoán
- Nhận định ngắn hạn: [Dựa trên tin tức thu thập]

---

## ⚠️ RỦI RO CẦN THEO DÕI
[Liệt kê 3-5 rủi ro chính trị có thể ảnh hưởng đến tài chính]

---

## 💡 KHUYẾN NGHỊ
[Đưa ra 2-3 khuyến nghị ngắn gọn cho nhà đầu tư cá nhân]

---
*Lưu ý: Đây là phân tích dựa trên AI, không phải tư vấn đầu tư chuyên nghiệp.*
"""

        try:
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            analysis_text = response.text
            
            # Estimate tokens (rough estimate for logging)
            estimated_tokens = len(prompt.split()) + len(analysis_text.split())
            
            # Save to database
            db.save_daily_report(
                report_date=today,
                news_summary=f"Phân tích {len(articles)} tin tức",
                political_analysis="Xem báo cáo đầy đủ",
                financial_predictions="Xem báo cáo đầy đủ",
                full_report=analysis_text
            )
            
            return {
                "success": True,
                "date": today,
                "articles_analyzed": len(articles),
                "report": analysis_text,
                "tokens_used": estimated_tokens  # Approximate
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "date": today
            }
    
    def get_quick_summary(self, articles: List[Dict]) -> str:
        """Generate a quick summary without full analysis (for testing)"""
        if not articles:
            return "Không có tin tức mới để tóm tắt."
        
        countries = {
            "US": [],
            "China": [],
            "Russia": [],
            "Japan": [],
            "Other": []
        }
        
        for article in articles:
            title_lower = article['title'].lower()
            if any(kw in title_lower for kw in ['usa', 'america', 'biden', 'trump', 'congress', 'white house']):
                countries["US"].append(article['title'])
            elif any(kw in title_lower for kw in ['china', 'chinese', 'beijing', 'xi']):
                countries["China"].append(article['title'])
            elif any(kw in title_lower for kw in ['russia', 'russian', 'putin', 'moscow']):
                countries["Russia"].append(article['title'])
            elif any(kw in title_lower for kw in ['japan', 'japanese', 'tokyo']):
                countries["Japan"].append(article['title'])
            else:
                countries["Other"].append(article['title'])
        
        summary = f"📊 Tóm tắt nhanh ({len(articles)} tin):\n\n"
        
        emoji_map = {"US": "🇺🇸", "China": "🇨🇳", "Russia": "🇷🇺", "Japan": "🇯🇵", "Other": "🌏"}
        
        for country, titles in countries.items():
            if titles:
                summary += f"{emoji_map[country]} {country}: {len(titles)} tin\n"
        
        return summary


# Create singleton instance
analyzer = AIAnalyzer()


if __name__ == "__main__":
    # Test with sample data
    from news_collector import collector
    
    print("Collecting news...")
    collector.collect_and_save()
    
    print("\nGetting articles for analysis...")
    articles = collector.get_articles_for_analysis(hours=24)
    
    print(f"\nQuick summary:")
    print(analyzer.get_quick_summary(articles))
    
    print("\n" + "="*50)
    print("Running full analysis (requires Gemini API key)...")
    
    if config.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        result = analyzer.analyze_news(articles)
        if result["success"]:
            print(f"\nAnalysis complete!")
            print("\n" + result["report"])
        else:
            print(f"\nAnalysis failed: {result['error']}")
    else:
        print("Skipping - Gemini API key not configured")
