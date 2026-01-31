"""
AI Analyzer Module - Uses Groq API (FREE) for news analysis
"""
from groq import Groq
from datetime import datetime
from typing import List, Dict
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
    
    def _format_articles_for_prompt(self, articles: List[Dict]) -> str:
        if not articles:
            return "Không có tin tức mới trong 24 giờ qua."
        
        formatted = []
        for i, article in enumerate(articles[:25], 1):
            formatted.append(f"""
{i}. [{article['source']} - {article['region']}]
   Tiêu đề: {article['title']}
   Link: {article.get('link', 'N/A')}
   Tóm tắt: {article.get('summary', 'N/A')[:200]}
""")
        return "\n".join(formatted)
    
    def _format_sources(self, articles: List[Dict]) -> str:
        """Format danh sách nguồn tin với link"""
        sources = []
        for i, article in enumerate(articles[:15], 1):
            title_short = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
            sources.append(f"{i}. [{article['source']}] {title_short}\n   🔗 {article.get('link', 'N/A')}")
        return "\n".join(sources)
    
    def analyze_news(self, articles: List[Dict]) -> Dict:
        today = datetime.now().strftime("%Y-%m-%d")
        articles_text = self._format_articles_for_prompt(articles)
        sources_text = self._format_sources(articles)
        
        prompt = f"""Bạn là chuyên gia phân tích chính trị và tài chính quốc tế.
Hôm nay là {today}. Dựa trên tin tức 24 giờ qua, hãy phân tích và dự đoán.

=== TIN TỨC ===
{articles_text}

=== YÊU CẦU ===
Viết báo cáo tiếng Việt theo cấu trúc:

## 📰 TIN TỨC CHÍNH TRỊ

### 🇺🇸 Hoa Kỳ
[Tóm tắt tin về Mỹ]

### 🇨🇳 Trung Quốc
[Tóm tắt tin về Trung Quốc]

### 🇷🇺 Nga
[Tóm tắt tin về Nga]

### 🇯🇵 Nhật Bản
[Tóm tắt tin về Nhật]

### 🌏 Khác
[Tin quan trọng khác]

---

## 📊 DỰ ĐOÁN TÀI CHÍNH (7-14 ngày)

### 🛢️ Giá dầu
- Xu hướng: [Tăng/Giảm/Đi ngang]
- Lý do: [Giải thích]

### 🥇 Giá vàng
- Xu hướng: [Tăng/Giảm/Đi ngang]
- Lý do: [Giải thích]

### 🏠 Bất động sản
- Nhận định: [Dựa trên chính sách tiền tệ]

### 📈 Chứng khoán
- Nhận định: [Dựa trên tin tức]

---

## ⚠️ RỦI RO CẦN THEO DÕI
[3-5 rủi ro chính]

---

## 💡 KHUYẾN NGHỊ
[2-3 khuyến nghị cho nhà đầu tư]

---
*Phân tích bởi AI, không phải tư vấn đầu tư chuyên nghiệp.*
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7
            )
            
            analysis_text = response.choices[0].message.content
            
            # Thêm phần nguồn tin vào cuối báo cáo
            full_report = f"""{analysis_text}

---

## 📎 NGUỒN TIN ({len(articles[:15])} bài)

{sources_text}
"""
            
            return {
                "success": True,
                "date": today,
                "articles_analyzed": len(articles),
                "report": full_report,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "date": today
            }
    
    def get_quick_summary(self, articles: List[Dict]) -> str:
        if not articles:
            return "Không có tin tức mới."
        return f"📊 Tóm tắt: {len(articles)} tin tức"


analyzer = AIAnalyzer()
