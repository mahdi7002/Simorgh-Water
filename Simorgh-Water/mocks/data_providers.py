"""
ارائه‌دهندگان داده شبیه‌سازی‌شده (Mock)
برای اجرا بدون سنسور واقعی و API خارجی.
الهام‌گرفته از حالت Demo پلتفرم‌های Digital Twin آب.
"""

from __future__ import annotations
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from core.models import WeatherCondition


class MockWeatherAPI:
    """شبیه‌ساز API هواشناسی (مشابه OpenWeather / هواشناسی ایران)"""

    def get_current(self, location: str) -> Dict[str, Any]:
        # شرایط واقعی‌تر برای یزد (خشک و گرم)
        conditions = [
            (WeatherCondition.CLEAR, 5, 15, 0),
            (WeatherCondition.CLOUDY, 40, 25, 0),
            (WeatherCondition.DUST, 10, 12, 0),
            (WeatherCondition.RAIN, 70, 45, random.uniform(1, 12)),
        ]
        cond, clouds, humidity, rain = random.choice(conditions)
        return {
            "condition": cond,
            "clouds": clouds + random.uniform(-5, 5),
            "humidity": max(5, min(90, humidity + random.uniform(-8, 8))),
            "rain": max(0, rain),
            "temperature": random.uniform(22, 42),
        }

    def get_forecast(self, location: str, hours_ahead: int) -> Dict[str, Any]:
        prob = random.uniform(0.05, 0.65)
        return {
            "rain_probability": prob,
            "rain_amount": random.uniform(0, 8) if prob > 0.4 else 0,
            "rain_time": (datetime.now() + timedelta(hours=random.randint(2, hours_ahead))).isoformat(),
            "rain_duration": random.randint(30, 180),
        }


class MockEnvironmentalSensors:
    """سنسورهای محیطی (خاک، رودخانه، سد)"""

    def get_environmental_data(self, location: str) -> Dict[str, float]:
        return {
            "soil_moisture": random.uniform(0.08, 0.55),
            "groundwater": random.uniform(15, 85),
            "river_flow": random.uniform(0.5, 12),
            "river_level": random.uniform(0.4, 3.2),
            "reservoir_level": random.uniform(22, 88),
            "reservoir_capacity": 120.0,  # میلیون مترمکعب (تقریبی برای یزد)
        }


class MockWaterCompanyAPI:
    """API شرکت آب و فاضلاب"""

    def get_real_time_data(self, city: str) -> Dict[str, Any]:
        population = 530000 if "یزد" in city else 200000
        supply = population * random.uniform(140, 190)
        leakage = random.uniform(0.12, 0.32)
        return {
            "population": population,
            "source": "سد + چاه",
            "supply": supply,
            "treatment_capacity": supply * 1.15,
            "treatment_efficiency": random.uniform(0.88, 0.97),
            "network_length": random.uniform(800, 2200),
            "consumption": supply * (1 - leakage * 0.3),
            "per_capita": random.uniform(135, 185),
            "wastewater": supply * 0.75,
            "treated_wastewater": supply * 0.75 * random.uniform(0.7, 0.95),
        }

    def get_historical_consumption(self, city: str, days: int = 90) -> List[float]:
        base = 160
        return [base + random.uniform(-25, 35) for _ in range(days)]


class MockNetworkSensors:
    """شبکه سنسورهای فشار و نشت"""

    def get_network_status(self, city: str) -> Dict[str, float]:
        return {
            "avg_pressure": random.uniform(1.6, 3.8),
            "leakage_rate": random.uniform(0.11, 0.29),
        }

    def get_zone_consumption(self, city: str) -> List[Dict[str, Any]]:
        zones = [
            {"name": "مرکز شهر", "consumption": 42000, "priority": 1},
            {"name": "بیمارستان‌ها", "consumption": 18000, "priority": 0},
            {"name": "مناطق مسکونی شرق", "consumption": 55000, "priority": 2},
            {"name": "صنعتی", "consumption": 31000, "priority": 3},
        ]
        return zones


class MockIoTDevices:
    """دستگاه‌های IoT داخل ساختمان"""

    def get_all_readings(self, building_id: str) -> Dict[str, Dict[str, float]]:
        return {
            "main_inlet": {
                "flow": random.uniform(0.5, 18),
                "pressure": random.uniform(1.8, 3.5),
                "temp": random.uniform(18, 28),
            },
            "kitchen": {"flow": random.uniform(0, 6)},
            "bathroom": {"flow": random.uniform(0, 12)},
            "toilet": {"flow": random.uniform(0, 4)},
            "washing": {"flow": random.uniform(0, 8)},
            "garden": {"flow": random.uniform(0, 5)},
            "drain": {
                "flow": random.uniform(0.4, 15),
                "temp": random.uniform(20, 35),
            },
        }

    def get_historical_data(self, building_id: str, days: int = 30) -> List[Dict]:
        return [{"day": i, "total_liters": random.uniform(180, 420)} for i in range(days)]


class MockQualitySensors:
    def get_measurements(self, building_id: str) -> Dict[str, float]:
        return {
            "tds": random.uniform(280, 650),
            "ph": random.uniform(6.8, 7.9),
            "chlorine": random.uniform(0.2, 0.8),
            "turbidity": random.uniform(0.1, 1.5),
        }


class MockWearableAPI:
    def get_data(self, user_id: str) -> Dict[str, Any]:
        return {
            "hydration": random.uniform(45, 95),
            "activity_level": random.choice(["sedentary", "moderate", "high"]),
            "sweat_loss": random.uniform(0.2, 1.8),
            "ambient_temp": random.uniform(24, 41),
        }


class MockHealthAppAPI:
    def get_data(self, user_id: str) -> Dict[str, Any]:
        intake = random.uniform(0.8, 3.2)
        return {
            "weight": random.uniform(55, 95),
            "water_intake": intake,
            "last_drink": datetime.now() - timedelta(hours=random.randint(1, 6)),
            "urine_color": random.choice(["pale", "yellow", "dark"]),
        }


class MockBaaranAI:
    """هسته حکمت و آگاهی — لایه منحصربه‌فرد سیمرغ"""

    WISDOM = [
        ("هر قطره آب، نشانه‌ای از رحمت است", "امروز یک لیوان آب را با حضور بنوش"),
        ("آب امانت است، نه ملک", "مصرف امروزت را با دیروز مقایسه کن"),
        ("زمین تشنه است چون ما غافلیم", "یک عادت کوچک صرفه‌جویی انتخاب کن"),
        ("بدن تو رودخانه‌ای کوچک است", "قبل از تشنگی، آب بنوش"),
        ("قنات‌های یزد هنوز نفس می‌کشند", "داستان یک قنات را برای کسی تعریف کن"),
    ]

    def analyze_spiritual_state(self, user_id: str) -> Dict[str, Any]:
        score = random.uniform(35, 92)
        if score < 45:
            level = "ناآگاه"
        elif score < 65:
            level = "آگاه"
        elif score < 82:
            level = "هوشیار"
        else:
            level = "حکیم"
        return {
            "awareness_level": level,
            "awareness_score": score,
        }

    def generate_wisdom_message(self, user_id: str, context: Dict = None) -> Dict[str, str]:
        title, action = random.choice(self.WISDOM)
        return {"title": title, "action": action}

    def recommend_action(self, user_id: str) -> str:
        return random.choice([
            "امروز دوش را به ۵ دقیقه محدود کن",
            "یک بطری آب همراه داشته باش",
            "شیر آب را هنگام مسواک بستن ببند",
            "به وضعیت سد شهر فکر کن",
            "یک جمله شکرگزاری برای آب بنویس",
        ])


# نمونه‌های آماده برای تزریق
weather_api = MockWeatherAPI()
env_sensors = MockEnvironmentalSensors()
water_company_api = MockWaterCompanyAPI()
network_sensors = MockNetworkSensors()
iot_devices = MockIoTDevices()
quality_sensors = MockQualitySensors()
wearable_api = MockWearableAPI()
health_api = MockHealthAppAPI()
baaran_ai = MockBaaranAI()