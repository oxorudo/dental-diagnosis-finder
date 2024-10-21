from rapidfuzz import process, fuzz
from Django.search.utils import unicode
import re

class HangulSearch:

    def __init__(self, dataframe):
        self.df = dataframe

    eng_to_kor = {
        'r': 'ㄱ', 'R': 'ㄲ', 's': 'ㄴ', 'e': 'ㄷ', 'E': 'ㄸ', 'f': 'ㄹ', 'a': 'ㅁ', 'q': 'ㅂ', 'Q': 'ㅃ', 't': 'ㅅ',
        'T': 'ㅆ', 'd': 'ㅇ', 'w': 'ㅈ', 'W': 'ㅉ', 'c': 'ㅊ', 'z': 'ㅋ', 'x': 'ㅌ', 'v': 'ㅍ', 'g': 'ㅎ',
        'k': 'ㅏ', 'o': 'ㅐ', 'i': 'ㅑ', 'O': 'ㅒ', 'j': 'ㅓ', 'p': 'ㅔ', 'u': 'ㅕ', 'P': 'ㅖ', 'h': 'ㅗ', 
        'y': 'ㅛ', 'n': 'ㅜ', 'b': 'ㅠ', 'm': 'ㅡ', 'l': 'ㅣ'
        }
    
    CHOSUNG_LIST = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
        ]
    
    def get_chosung(self, text): # 데이터프레임 값들 초성 변환
        result = []
        text = text.replace(" ", "")  # 공백 제거
        for char in str(text):
            if 44032 <= ord(char) <= 55203:
                index = (ord(char) - 44032) // 588
                result.append(self.CHOSUNG_LIST[index])
            else:
                result.append(char)
        return ''.join(result)

    def convert_eng_to_kor(self, eng_text): # 한영 변환
        return ''.join(self.eng_to_kor.get(char, char) for char in eng_text)

    def is_chosung(self, text): #  검색어가 초성인지 판별
        text = text.replace(" ", "")  # 공백 제거
        return all(char in self.CHOSUNG_LIST for char in str(text))

    def search_with_contains(self, data, query): # 보정 전 검색어 포함 여부 검색, 공백 무시하고 검색
        normalized_query = re.sub(r'\s+', '', query)
        return [item for item in data if normalized_query in re.sub(r'\s+', '', item).upper()] # 데이터 전체 대문자로 바꿔서 검색

    def search_with_partial_and_correction(self, data, query, threshold=60): # 유사한 검색어들 반환
        matches = process.extract(query, data, scorer=fuzz.partial_ratio, limit=15)
        return [match[0] for match in matches if match[1] >= threshold]

    def search_with_chosung_inclusion(self, data, query): # 초성 검색
        chosung_query = self.get_chosung(query)
        return [item for item in data if chosung_query in self.get_chosung(item)]
    
    def clean_text(self, query):
        return re.sub(r'\s+', ' ', query.strip())  # 중복 공백을 단일 공백으로 변환

    def search_with_options(self, data, query): # 검색 옵션

        if self.is_chosung(query): # 초성 검색어면 초성 검색 모드, 소문자 영어 검색어면 한영 변환 검색
            print('초성 검색 실행')
            return self.search_with_chosung_inclusion(data, query)

        if all(char.isalpha() and char.islower() for char in query):
            print('한영 변환 검색 실행')
            query = unicode.join_jamos(self.convert_eng_to_kor(query)) # 한국어 풀어쓰기 해제
            print(query)
            return self.search_with_contains(self.df.apply(lambda col: col.map(str)).values.flatten(), query)

        print('유사도 검색 실행')
        return self.search_with_partial_and_correction(data, query) 

    def search_df_with_options(self, query): # 보정 전에 순수 검색어로 검색 후 결과 없으면 보정 검색하는 옵션

        query = query.upper()

        self.df = self.df.apply(lambda col: col.map(lambda x: self.clean_text(str(x))))
        
        results = self.search_with_contains(self.df.apply(lambda col: col.map(str)).values.flatten(), query)
        if not results:
            query = query.lower()

            print('보정 후 검색') 
            print(query)
            for column in self.df.columns:
                col_results = self.search_with_options(self.df[column].apply(str).tolist(), query)
                print(col_results)
                if col_results:
                    results.extend(col_results)

        unique_results = set(results)
        return self.df[self.df.apply(lambda row: any(str(row[col]) in unique_results for col in self.df.columns), axis=1)]
    
