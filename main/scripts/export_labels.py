"""
Експорт розмічених даних з Label Studio до структурованого формату.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd
import yaml
from loguru import logger


class LabelExporter:
    """Експортер розмічених даних."""
    
    def __init__(self, config_path: str = "params.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
            
        self.export_format = self.config['labeling']['export_format']
        self.include_metadata = self.config['labeling']['include_metadata']
    
    def export_from_label_studio(self, input_path: str, output_path: str):
        """Експортує дані з Label Studio формату."""
        
        # Читаємо експорт з Label Studio
        with open(input_path, 'r', encoding='utf-8') as f:
            label_studio_export = json.load(f)
        
        processed_data = []
        
        for item in label_studio_export:
            # Витягуємо основні дані
            text = item['data']['text']
            item_id = item['data'].get('id', '')
            
            # Витягуємо анотації
            annotations = item.get('annotations', [])
            
            if annotations:
                # Беремо першу анотацію (в реальному проекті може бути консенсус)
                annotation = annotations[0]
                results = annotation.get('result', [])
                
                if results:
                    # Витягуємо мітку тональності
                    sentiment_result = results[0]
                    sentiment = sentiment_result['value']['choices'][0]
                    
                    processed_item = {
                        'id': item_id,
                        'text': text,
                        'sentiment': sentiment,
                        'annotation_id': annotation['id'],
                        'completed_at': annotation.get('completed_at', ''),
                        'annotation_time': annotation.get('lead_time', 0)
                    }
                    
                    if self.include_metadata:
                        metadata = json.loads(item['data'].get('metadata', '{}'))
                        processed_item['metadata'] = metadata
                    
                    processed_data.append(processed_item)
            else:
                # Зразок без розмітки
                processed_item = {
                    'id': item_id,
                    'text': text,
                    'sentiment': None,
                    'annotation_id': None,
                    'completed_at': None,
                    'annotation_time': None
                }
                processed_data.append(processed_item)
        
        # Зберігаємо результат
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if self.export_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        # Додатково зберігаємо як CSV
        df = pd.DataFrame(processed_data)
        csv_path = output_path.replace('.json', '.csv')
        df.to_csv(csv_path, index=False)
        
        logger.info(f"Експортовано {len(processed_data)} зразків")
        logger.info(f"Розмічено: {len([x for x in processed_data if x['sentiment']])}")
        logger.info(f"Збережено: {output_path}")
        
        return processed_data


def main():
    """Головна функція експорту."""
    
    logger.info("📤 Початок експорту розмітки")
    
    exporter = LabelExporter()
    
    # Шлях до експорту з Label Studio
    input_path = "data/raw/label_studio_export.json"
    output_path = "data/labeled/annotations.json"
    
    if os.path.exists(input_path):
        exporter.export_from_label_studio(input_path, output_path)
        logger.info("✅ Експорт завершено успішно!")
    else:
        logger.warning(f"Файл експорту не знайдено: {input_path}")
        logger.info("Створюю приклад розмічених даних для демонстрації...")
        
        # Створюємо приклад для демонстрації
        demo_data = [
            {
                'id': 'sample_0001',
                'text': 'Це чудовий продукт, дуже задоволений покупкою!',
                'sentiment': 'positive',
                'annotation_id': 'demo_001',
                'completed_at': '2025-06-25T10:30:00Z',
                'annotation_time': 15.5
            },
            {
                'id': 'sample_0002', 
                'text': 'Жахливий сервіс, ніколи більше не буду користуватись.',
                'sentiment': 'negative',
                'annotation_id': 'demo_002',
                'completed_at': '2025-06-25T10:31:00Z',
                'annotation_time': 12.3
            },
            {
                'id': 'sample_0003',
                'text': 'Звичайний товар, нічого особливого.',
                'sentiment': 'neutral',
                'annotation_id': 'demo_003', 
                'completed_at': '2025-06-25T10:32:00Z',
                'annotation_time': 18.7
            }
        ]
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Створено демо-дані: {output_path}")


if __name__ == "__main__":
    main()