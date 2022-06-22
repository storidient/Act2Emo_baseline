from data.utils import Rx, B

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

unify_dict = {
    'quotation' : Rx('[“”]', '"', 1),
    'apostrophe' : Rx('[‘’]', "'", 1),
    'middle' : Rx('[ㆍㆍ]', ',', 1),
    'hyphen' : Rx('[─ㅡ⎯―\—]', '-', 1),
    'ellipsis' : Rx('\.\.\.+|‥+|…', '⋯', 1)
}

default = {
    'wrong_bracket' : Rx('&lt;|&gt;', '', 100)
}
