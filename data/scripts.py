from data.utils import B

letter = {
    'korean' : '[가-힣]',
    'english': '[A-Za-z]',
    'chinese' : '[一-鿕㐀-䶵豈-龎]',
    'imperfect': '[ㄱ-ㅎ]',
    'number' : '[0-9]'
    }

bracket = {
    'small' :  B('\(', '\)'),
    'inequal' : B('<', '>'),
    'inequal-1': B('〈','〉'),
    'middle' : B('\[','\]'),
    'middle-1' : B('〔', '〕'),
    'big' : B('{', '}'),
    'sickle' : B('「', '」'),
    'double_sickle' : B('『','』')
    }
