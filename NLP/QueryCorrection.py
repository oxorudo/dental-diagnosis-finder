from rapidfuzz import process, fuzz
import unicode

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
    
    def get_chosung(self, text):
        result = []
        for char in str(text):
            if 44032 <= ord(char) <= 55203:
                index = (ord(char) - 44032) // 588
                result.append(self.CHOSUNG_LIST[index])
            else:
                result.append(char)
        return ''.join(result)

    def convert_eng_to_kor(self, eng_text):
        return ''.join(self.eng_to_kor.get(char, char) for char in eng_text)

    def is_chosung(self, text):
        return all(char in self.CHOSUNG_LIST for char in str(text))

    def search_with_contains(self, data, query):
        return [item for item in data if query in item]

    def search_with_partial_and_correction(self, data, query, threshold=60):
        matches = process.extract(query, data, scorer=fuzz.partial_ratio, limit=15)
        return [match[0] for match in matches if match[1] >= threshold]

    def search_with_chosung_inclusion(self, data, query):
        chosung_query = self.get_chosung(query)
        return [item for item in data if chosung_query in self.get_chosung(item)]

    def search_with_options(self, data, query):
        if query.startswith('K'):
            return self.search_with_contains(data, query[1:])

        if self.is_chosung(query):
            return self.search_with_chosung_inclusion(data, query)

        if all(char.isalpha() and char.islower() for char in query):
            query = unicode.join_jamos(self.convert_eng_to_kor(query))

        return self.search_with_partial_and_correction(data, query)

    def search_df_with_options(self, query):
        results = self.search_with_contains(self.df.applymap(str).values.flatten(), query)
        if not results:
            for column in self.df.columns:
                col_results = self.search_with_options(self.df[column].apply(str).tolist(), query)
                if col_results:
                    results.extend(col_results)

        unique_results = set(results)
        return self.df[self.df.apply(lambda row: any(str(row[col]) in unique_results for col in self.df.columns), axis=1)]
