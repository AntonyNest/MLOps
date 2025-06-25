# Модуль містить скрипти для обробки даних та управління ML пайплайном.


__version__ = "1.0.0"
__author__ = "Дмитро Сподарець"
__email__ = "dmytro.spodarets@example.com"

from loguru import logger

# Налаштування логування
logger.add(
    "logs/mlops_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
)

logger.info("MLOps Data Platform ініціалізовано")

# Label Studio XML Configuration

#Конфігурація для Label Studio - розмітка тональності тексту

#Розмістіть цей XML в налаштуваннях проекту Label Studio:

LABEL_STUDIO_CONFIG = """
<View>
    <Header value="Розмітка тональності українського тексту"/>
    <Text name="text" value="$text"/>
    
    <View style="display: flex; flex-direction: row; align-items: flex-start;">
        <View style="flex: 1; margin-right: 20px;">
            <Text name="instructions" 
                  value="Оцініть тональність наступного тексту:"
                  style="font-weight: bold; margin-bottom: 10px;"/>
            
            <Choices name="sentiment" toName="text" choice="single-radio" showInline="true">
                <Choice value="positive" html=" Позитивна" style="color: green;"/>
                <Choice value="negative" html=" Негативна" style="color: red;"/>
                <Choice value="neutral" html=" Нейтральна" style="color: gray;"/>
            </Choices>
        </View>
        
        <View style="flex: 1;">
            <Text name="confidence_label" 
                  value="Оцініть впевненість у своєму рішенні:"
                  style="font-weight: bold; margin-bottom: 10px;"/>
            
            <Rating name="confidence" toName="text" maxRating="5" defaultValue="2"
                    size="medium" icon="star"/>
            
            <TextArea name="comment" toName="text" 
                      placeholder="Коментар (опціонально)"
                      rows="3"/>
        </View>
    </View>
    
    <Text name="metadata" value="$metadata" hidden="true"/>
    <Text name="id" value="$id" hidden="true"/>
</View>
"""
