"""تنظیمات مرکزی — بدون pydantic-settings"""

class Settings:
    APP_NAME: str = "Simorgh Water Cycle"
    APP_VERSION: str = "1.2.0"
    APP_DESCRIPTION: str = "سیستم جامع مدیریت چرخه آب — هشدار رنگی + اقدام روزانه"
    DEFAULT_CITY: str = "یزد"
    DEFAULT_LAT: float = 31.8974
    DEFAULT_LON: float = 54.3569
    LEAKAGE_WARNING_THRESHOLD: float = 0.15
    LEAKAGE_CRITICAL_THRESHOLD: float = 0.25
    RESERVOIR_LOW_THRESHOLD: float = 0.30
    HYDRATION_WARNING: float = 70.0
    SOIL_MOISTURE_DROUGHT: float = 0.20
    TARGET_PER_CAPITA_LITERS: float = 150.0
    MOCK_MODE: bool = True
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 8080

settings = Settings()
