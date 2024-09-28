from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer
import joblib
import pickle
from sentence_transformers.util import cos_sim
from dataclasses import dataclass


@dataclass
class Feedback:
    class1: str
    class2: str
    answer: str


class PredictModel:
    tfidf_high: TfidfVectorizer
    logreg_high: LogisticRegression

    model_level2 = {
        'МОДЕРАЦИЯ': 0,
        'МОНЕТИЗАЦИЯ': 0,
        'УПРАВЛЕНИЕ АККАУНТОМ': 0,
        'ДОСТУП К RUTUBE': None,
        'ПРЕДЛОЖЕНИЯ': 0,
        'ВИДЕО': 0,
        'ТРАНСЛЯЦИЯ': 0,
        'СОТРУДНИЧЕСТВО ПРОДВИЖЕНИЕ РЕКЛАМА': None,
        'ПОИСК': 0,
        'БЛАГОТВОРИТЕЛЬНОСТЬ ДОНАТЫ': None,
    }

    one_class = {
        'ДОСТУП К RUTUBE': 'Приложение\xa0',
        'СОТРУДНИЧЕСТВО ПРОДВИЖЕНИЕ РЕКЛАМА': 'Продвижение канал',
        'БЛАГОТВОРИТЕЛЬНОСТЬ ДОНАТЫ': 'Подключение/отключение донатов',
    }

    model_embed: SentenceTransformer
    faq_embeddings: dict
    faq_answers: dict

    def __init__(self, folder="models/"):
        # Init high level models

        print("----- INIT START ------")
        self.logreg_high = joblib.load(f'{folder}logreg_high.pkl')
        self.tfidf_high = joblib.load(f'{folder}tfidf_high.pkl')

        print("Level 1 inited")
        # Init second level models

        for key, models in self.model_level2.items():
            if models is not None:
                cur_logreg = joblib.load(f'{folder}{key}_logreg.pkl')
                cur_tfidf = joblib.load(f'{folder}{key}_tfidf.pkl')

                self.model_level2[key] = (cur_tfidf, cur_logreg)

        print("Level 2 inited")
        # Init embedding model

        self.model_embed = SentenceTransformer("ai-forever/sbert_large_nlu_ru")

        with open(f'{folder}embeddings_dict.pkl', 'rb') as f:
            self.faq_embeddings = pickle.load(f)

        with open(f'{folder}answers_dict.pkl', 'rb') as f:
            self.faq_answers = pickle.load(f)

        print("Level 3 inited")

    def inference(self, sentence):
        tfidf_high_sent = self.tfidf_high.transform([sentence])
        pred_level1 = self.logreg_high.predict(tfidf_high_sent)[0]

        tfidf_2lvl_sent = self.model_level2[pred_level1][0].transform([sentence])
        pred_level2 = self.model_level2[pred_level1][1].predict(tfidf_2lvl_sent)[0]

        question_embedding = self.model_embed.encode(sentence)

        similarities = cos_sim(question_embedding, self.faq_embeddings[pred_level2])
        answer = self.faq_answers[pred_level2][similarities.argmax().item()]

        return Feedback(class1=pred_level1, class2=pred_level2, answer=answer)




