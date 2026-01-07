import logging

logger = logging.getLogger(__name__)


class DocumentClassifier:
    def __init__(self):
        self.rules = {
            "УПД": [
                "универсальный передаточный документ",
                "статус",
                "упд"
            ],
            "СЧЕТ_ФАКТУРА": [
                "счет-фактура",
                "счет фактура",
                "исправление №"
            ],
            "ТОРГ-12": [
                "торг-12",
                "форма по окуд 0330212",
                "товарная накладная"
            ]
        }

        logger.info("Классификатор документов инициализирован")

    def classify(self, text: str) -> str:
        if not text:
            return "НЕИЗВЕСТНО"

        text = text.lower()

        scores = {
            "УПД": 0,
            "СЧЕТ_ФАКТУРА": 0,
            "ТОРГ-12": 0
        }

        for doc_type, keywords in self.rules.items():
            for kw in keywords:
                if kw in text:
                    scores[doc_type] += 1

        # приоритет УПД
        if scores["УПД"] > 0:
            return "УПД"

        # далее по количеству совпадений
        best = max(scores, key=scores.get)

        if scores[best] == 0:
            return "НЕИЗВЕСТНО"

        return best


classifier = DocumentClassifier()


def classify_document(text: str) -> str:
    return classifier.classify(text)
