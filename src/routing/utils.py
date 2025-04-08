from typing import Dict

def get_russian_forms(object_name: str, gender: str) -> Dict[str, str]:
    forms = {
        'm': {
            'именительный': object_name,
            'родительный': f'{object_name}а',
            'винительный': object_name,
            'творительный': f'{object_name}ом',
            'plural': f'{object_name}ы',
            'genitive_plural': f'{object_name}ов',  
            'найден': 'найден',
            'удален': 'удален',
            'создан': 'создан'
        },
        'f': {
            'именительный': object_name,
            'родительный': f'{object_name}и',
            'винительный': f'{object_name}у',
            'творительный': f'{object_name}ой',
            'plural': f'{object_name}ы',
            'genitive_plural': f'{object_name}',
            'найден': 'найдена',
            'удален': 'удалена',
            'создан': 'создана'
        },
        'n': {
            'именительный': object_name,
            'родительный': f'{object_name}а',
            'винительный': object_name,
            'творительный': f'{object_name}ом',
            'plural': f'{object_name}а',
            'genitive_plural': f'{object_name}',
            'найден': 'найдено',
            'удален': 'удалено',
            'создан': 'создано'
        }
    }
    return forms[gender]
