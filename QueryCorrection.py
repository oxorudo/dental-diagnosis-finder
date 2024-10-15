
from unicode import join_jamos
from rapidfuzz import process, fuzz

class HangulSearch:
    eng_to_kor_dict = {
        'r': 'ㄱ', 'R': 'ㄲ', 's': 'ㄴ', 'e': 'ㄷ', 'E': 'ㄸ', 'f': 'ㄹ', 'a': 'ㅁ', 'q': 'ㅂ', 'Q': 'ㅃ', 't': 'ㅅ',
        'T': 'ㅆ', 'd': 'ㅇ', 'w': 'ㅈ', 'W': 'ㅉ', 'c': 'ㅊ', 'z': 'ㅋ', 'x': 'ㅌ', 'v': 'ㅍ', 'g': 'ㅎ',
        'k': 'ㅏ', 'o': 'ㅐ', 'i': 'ㅑ', 'O': 'ㅒ', 'j': 'ㅓ', 'p': 'ㅔ', 'u': 'ㅕ', 'P': 'ㅖ', 'h': 'ㅗ', 
        'y': 'ㅛ', 'n': 'ㅜ', 'b': 'ㅠ', 'm': 'ㅡ', 'l': 'ㅣ'
    }

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def convert_eng_to_kor(self, eng_text):
        """영어 입력을 한글 자모로 변환하는 함수"""
        return ''.join(self.eng_to_kor_dict.get(char, char) for char in eng_text)

    def correct_query(self, query):
        """검색어를 DataFrame의 데이터를 참고하여 보정하는 함수"""
        if all(char.isalpha() and char.islower() for char in query):  # 모든 문자가 알파벳 소문자인 경우 한글로 변환
            query = join_jamos(self.convert_eng_to_kor(query))

        # max_score = 0
        # corrected = query
        # for column in self.dataframe.columns:
        #     closest_match = process.extractOne(query, self.dataframe[column], scorer=fuzz.WRatio)
        #     if closest_match and closest_match[1] > max_score:
        #         max_score = closest_match[1]
        #         corrected = closest_match[0] if max_score > 50 else query  # 유사도 75% 이상인 경우만 반환

        # return corrected
        max_score = 0
        corrected = query
        for column in self.dataframe.columns:
            closest_match = process.extractOne(query, self.dataframe[column], scorer=fuzz.WRatio)
            if closest_match and closest_match[1] > max_score:
                max_score = closest_match[1]
                corrected = closest_match[0] if max_score > 50 else query  # 유사도 50% 이상인 경우만 반환

        return corrected