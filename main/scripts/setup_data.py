"""
Ініціалізація датасету для розмітки тональності тексту.
"""

import json
import os
import random
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import yaml
from loguru import logger

class DatasetInitializer:
    """Ініціалізатор датасету з Domain-Driven підходом."""
    
    def __init__(self, config_path: str = "params.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.sample_size = self.config['prepare']['sample_size']
        self.validation_split = self.config['prepare']['validation_split']
        self.random_seed = self.config['prepare']['random_seed']
        
        random.seed(self.random_seed)
        
    def create_sample_texts(self) -> List[Dict[str, Any]]:
        """Створює зразки текстів для розмітки."""
        
        # Приклади текстів різної тональності (для демонстрації)
        sample_texts = [
            "Це чудовий продукт, дуже задоволений покупкою!",
            "Жахливий сервіс, ніколи більше не буду користуватись.",
            "Звичайний товар, нічого особливого.",
            "Просто фантастично! Рекомендую всім друзям.",
            "Могло б бути і краще, але в цілому непогано.",
            "Повна катастрофа, гроші на вітер.",
            "Нейтральне враження, ні добре, ні погано.",
            "Вражений якістю та швидкістю доставки!",
            "Сервіс підкачав, але продукт гарний.",
            "Ідеально підійшло для моїх потреб."
        ]
        
        # Генеруємо додаткові варіації
        dataset = []
        for i in range(self.sample_size):
            base_text = random.choice(sample_texts)
            
            # Додаємо варіації для збільшення різноманітності
            variations = [
                base_text,
                f"Відгук: {base_text}",
                f"{base_text} Дякую!",
                f"Моя думка: {base_text}",
            ]
            
            text = random.choice(variations)
            
            dataset.append({
                "id": f"sample_{i:04d}",
                "text": text,
                "source": "synthetic",
                "created_at": "2025-06-25T10:00:00Z",
                "metadata": {
                    "length": len(text),
                    "words_count": len(text.split()),
                    "language": "uk"
                }
            })
            
        return dataset
    
    def save_dataset(self, dataset: List[Dict], output_path: str):
        """Зберігає датасет у форматі для Label Studio."""
        
        # Створюємо директорії
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Конвертуємо в формат Label Studio
        label_studio_format = []
        for item in dataset:
            label_studio_format.append({
                "data": {
                    "text": item["text"],
                    "id": item["id"],
                    "metadata": json.dumps(item["metadata"])
                }
            })
        
        # Зберігаємо JSON для Label Studio
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(label_studio_format, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Датасет збережено: {output_path}")
        logger.info(f"Кількість зразків: {len(dataset)}")
        
        # Також зберігаємо як CSV для аналізу
        df = pd.DataFrame(dataset)
        csv_path = output_path.replace('.json', '.csv')
        df.to_csv(csv_path, index=False)
        logger.info(f"CSV версія: {csv_path}")


def main():
    """Головна функція ініціалізації."""
    
    logger.info("🚀 Початок ініціалізації датасету")
    
    initializer = DatasetInitializer()
    dataset = initializer.create_sample_texts()
    
    # Зберігаємо в директорію prepared
    output_path = "data/prepared/sentiment_dataset.json"
    initializer.save_dataset(dataset, output_path)
    
    logger.info("✅ Ініціалізація завершена успішно!")


if __name__ == "__main__":
    main()