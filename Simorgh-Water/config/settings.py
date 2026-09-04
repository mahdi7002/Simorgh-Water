"""
تنظیمات مرکزی سیستم مدیریت چرخه آب سیمرغ
الهام‌گرفته از معماری پلتفرم‌های Xylem Vue و Bentley WaterSight
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # هویت پروژه
    APP_NAME: str = "Simorgh Water Cycle"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "سیستم جامع مدیریت چرخه کامل آب — از آسمان تا روح"
    
    # مکان پیش‌فرض (یزد)
    DEFAULT_CITY: str = "یزد"
    DEFAULT_LAT: float = 31.8974
    DEFAULT_LON: float = 54.3569
    
    # آستانه‌های هشدار (بر اساس استانداردهای جهانی آب)
    LEAKAGE_WARNING_THRESHOLD: float = 0.15      # ۱۵٪ نشت = هشدار
    LEAKAGE_CRITICAL_THRESHOLD: float = 0.25     # ۲۵٪ نشت = بحرانی
    RESERVOIR_LOW_THRESHOLD: float = 0.30        # ۳۰٪ ظرفیت سد
    HYDRATION_WARNING: float = 70.0              # درصد آبرسانی بدن
    SOIL_MOISTURE_DROUGHT: float = 0.20
    
    # مصرف سرانه هدف (لیتر/نفر/روز) — استاندارد ایران و WHO
    TARGET_PER_CAPITA_LITERS: float = 150.0
    
    # حالت شبیه‌سازی (بدون نیاز به سنسور واقعی)
    MOCK_MODE: bool = True
    
    # داشبورد
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 8080
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()