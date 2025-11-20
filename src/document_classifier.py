import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class DocumentClassifier:
    
    def __init__(self):
        self.unique_keywords = {
            'УПД': [
                'универсальный передаточный документ',
                'статус: [1]',
                'статус: [2]',
                '1 – счет-фактура и передаточный документ'
            ],
            'ТОРГ-12': [
                'торг-12',
                'унифицированная форма № торг-12', 
                'форма по окуд 0330212',
                'коды окуд 0330212'
            ],
            'СЧЕТ_ФАКТУРА': [
                'счет-фактура №',
                'приложение к постановлению правительства рф № 1137',
                'исправление № – от –'
            ]
        }
        
        logger.info("Классификатор документов инициализирован")

    def classify(self, extracted_text: str) -> Tuple[str, float]:
        if not extracted_text:
            logger.warning("Получен пустой текст для классификации")
            return "НЕИЗВЕСТНО", 0.0
        
        text_lower = extracted_text.lower()
        logger.debug(f"Анализируем текст: {text_lower[:200]}...")
        
        found_types = []
        
        for doc_type, keywords in self.unique_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    logger.info(f"Найдено ключевое слово для {doc_type}: '{keyword}'")
                    found_types.append(doc_type)
                    break
        
        if len(found_types) == 1:
            doc_type = found_types[0]
            logger.info(f"Документ классифицирован как: {doc_type}")
            return doc_type, 95.0
        elif len(found_types) > 1:
            types_str = ", ".join(found_types)
            logger.warning(f"Неоднозначность: найдены типы: {types_str}")
            return "НЕИЗВЕСТНО", 0.0
        else:
            logger.warning("Не найдено ключевых слов для известных типов")
            return "НЕИЗВЕСТНО", 0.0

    def get_supported_types(self) -> list:
        return list(self.unique_keywords.keys())

classifier = DocumentClassifier()

def classify_document(text: str) -> Tuple[str, float]:
    return classifier.classify(text)
