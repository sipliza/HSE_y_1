import re

def check_car_id(car_id: str) -> str:
    translit_map = str.maketrans('ABEKMHOPCTXabekmhopctx', 'АВЕКМНОРСТХавекмнорстх')
    
    normalized_id = car_id.strip().upper().translate(translit_map)
    
    pattern = r'^([АВЕКМНОРСТУХ])(\d{3})([АВЕКМНОРСТУХ]{2})(\d{2,3})$'
    
    match = re.match(pattern, normalized_id)
    
    if match:
        letter1, digits, letters2, region = match.groups()
        # Собираем основную часть номера без региона
        main_part = f"{letter1}{digits}{letters2}"
        return f"Номер {main_part} валиден. Регион: {region}."
    else:
        return "Номер не валиден."