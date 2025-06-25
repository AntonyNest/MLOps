"""
Валідація якості розмічених даних.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

import yaml
from loguru import logger


class DataValidator:
    """Валідатор якості даних."""
    
    def __init__(self, config_path: str = "params.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
            
        self.min_samples = self.config['validation']['min_samples']
        self.quality_threshold = self.config['validation']['quality_threshold']
        self.required_labels = self.config['validation']['required_labels']
    
    def validate_dataset(self, data_path: str) -> Dict[str, Any]:
        """Валідує датасет і повертає метрики якості."""
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metrics = {}
        
        # Базові метрики
        total_samples = len(data)
        labeled_samples = len([x for x in data if x.get('sentiment')])
        unlabeled_samples = total_samples - labeled_samples
        
        metrics['total_samples'] = total_samples
        metrics['labeled_samples'] = labeled_samples 
        metrics['unlabeled_samples'] = unlabeled_samples
        metrics['labeling_coverage'] = labeled_samples / total_samples if total_samples > 0 else 0
        
        # Перевірка мінімальної кількості зразків
        metrics['meets_min_samples'] = labeled_samples >= self.min_samples
        
        # Розподіл міток
        label_distribution = {}
        for item in data:
            sentiment = item.get('sentiment')
            if sentiment:
                label_distribution[sentiment] = label_distribution.get(sentiment, 0) + 1
        
        metrics['label_distribution'] = label_distribution
        
        # Перевірка наявності всіх необхідних міток
        missing_labels = set(self.required_labels) - set(label_distribution.keys())
        metrics['missing_labels'] = list(missing_labels)
        metrics['has_all_required_labels'] = len(missing_labels) == 0
        
        # Баланс класів
        if label_distribution:
            max_count = max(label_distribution.values())
            min_count = min(label_distribution.values())
            metrics['class_balance_ratio'] = min_count / max_count if max_count > 0 else 0
        else:
            metrics['class_balance_ratio'] = 0
        
        # Якість анотацій (середній час анотації)
        annotation_times = [x.get('annotation_time', 0) for x in data if x.get('annotation_time')]
        if annotation_times:
            metrics['avg_annotation_time'] = sum(annotation_times) / len(annotation_times)
            metrics['annotation_quality_score'] = min(1.0, 30.0 / metrics['avg_annotation_time'])
        else:
            metrics['avg_annotation_time'] = 0
            metrics['annotation_quality_score'] = 0
        
        # Загальна оцінка якості
        quality_factors = [
            metrics['labeling_coverage'],
            1.0 if metrics['meets_min_samples'] else 0.0,
            1.0 if metrics['has_all_required_labels'] else 0.0,
            metrics['class_balance_ratio'],
            metrics['annotation_quality_score']
        ]
        
        metrics['overall_quality_score'] = sum(quality_factors) / len(quality_factors)
        metrics['passes_quality_threshold'] = metrics['overall_quality_score'] >= self.quality_threshold
        
        return metrics
    
    def save_metrics(self, metrics: Dict[str, Any], output_path: str):
        """Зберігає метрики якості."""
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Метрики збережено: {output_path}")
    
    def print_report(self, metrics: Dict[str, Any]):
        """Виводить звіт про якість даних."""
        
        logger.info("Звіт про якість даних:")
        logger.info(f"   Загальна кількість зразків: {metrics['total_samples']}")
        logger.info(f"   Розмічених зразків: {metrics['labeled_samples']}")
        logger.info(f"   Покриття розмітки: {metrics['labeling_coverage']:.2%}")
        logger.info(f"   Розподіл міток: {metrics['label_distribution']}")
        logger.info(f"   Баланс класів: {metrics['class_balance_ratio']:.2f}")
        logger.info(f"   Середній час анотації: {metrics['avg_annotation_time']:.1f}s")
        logger.info(f"   Загальна оцінка якості: {metrics['overall_quality_score']:.2%}")
        
        if metrics['passes_quality_threshold']:
            logger.info("Датасет відповідає вимогам якості!")
        else:
            logger.warning("Датасет не відповідає вимогам якості.")
            
            if not metrics['meets_min_samples']:
                logger.warning(f"   Потрібно мінімум {self.min_samples} розмічених зразків")
            
            if not metrics['has_all_required_labels']:
                logger.warning(f"   Відсутні мітки: {metrics['missing_labels']}")


def main():
    """Головна функція валідації."""
    
    logger.info("Початок валідації даних")
    
    validator = DataValidator()
    
    data_path = "data/labeled/annotations.json"
    metrics_path = "metrics/data_quality.json"
    
    if os.path.exists(data_path):
        metrics = validator.validate_dataset(data_path)
        validator.save_metrics(metrics, metrics_path)
        validator.print_report(metrics)
        
        logger.info("Валідація завершена!")
    else:
        logger.error(f"Файл даних не знайдено: {data_path}")
        logger.info("Спочатку виконайте експорт розмітки.")


if __name__ == "__main__":
    main()