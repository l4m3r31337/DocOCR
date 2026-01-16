import logging

logger = logging.getLogger(__name__)

class DocumentClassifier:
    
    def __init__(self):
        self.unique_keywords = {
            'УПД': [
                'универсальный передаточный документ',
                'универсальный'
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

    def classify(self, extracted_text: str) -> str:
        if not extracted_text:
            logger.warning("Получен пустой текст для классификации")
            return "НЕИЗВЕСТНО"

        text_lower = extracted_text.lower()
        logger.debug(f"Анализируем текст: {text_lower[:200]}...")

        found_types = []

        for doc_type, keywords in self.unique_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    logger.info(f"Найдено ключевое слово для {doc_type}: '{keyword}'")
                    found_types.append(doc_type)
                    break

        if not found_types:
            logger.warning("Не найдено ключевых слов для известных типов")
            return "НЕИЗВЕСТНО"

        if "УПД" in found_types and "СЧЕТ_ФАКТУРА" in found_types:
            logger.info("УПД имеет приоритет над счетом-фактурой")
            return "УПД"
        elif "ТОРГ-12" in found_types and "СЧЕТ_ФАКТУРА" in found_types:
            logger.info("ТОРГ-12 имеет приоритет")
            return "ТОРГ-12"
        elif len(found_types) == 1:
            doc_type = found_types[0]
            logger.info(f"Документ классифицирован как: {doc_type}")
            return doc_type
        else:
            logger.info(f"Неоднозначность, возвращаем первый тип: {found_types[0]}")
            return found_types[0]

    def get_supported_types(self) -> list:
        return list(self.unique_keywords.keys())

classifier = DocumentClassifier()

def classify_document(text: str) -> str:
    return classifier.classify(text)