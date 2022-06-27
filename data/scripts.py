from data.utils import Rx, B

ep_pattern_dict = {
    'N화' : '.*[0-9]+[화].*',
    '<N 제목>' : '<.*[0-9]+[^가-힣]+>$',
    '영어 N' : '^[A-Za-z]+[^가-힣]*[0-9]+.*',
    'N. 제목 ': '^[^“"].*[0-9]+\. ?[^가-힣0-9%]+.*',
}

ep_pattern_dict['키워드'] = ''.join(
    ['.*%s ?[^가-힣]+.*|.*%s$' % (x, x) for x in ['에필로그',
                                                '프롤로그', 
                                                '본편']]
)

scene_pattern_dict = {
    '*' : '\*+',
    '+' : '\++',
}

letter_dict = {
    'korean' : '가-힣',
    'english': 'A-Za-z',
    'chinese' : '一-鿕㐀-䶵豈-龎',
    'imperfect': 'ㄱ-ㅎ',
    'number' : '0-9'
    }

bracket_dict = {
    'small' :  B('\(', '\)'),
    'inequal' : B('<', '>'),
    'inequal-1': B('〈','〉'),
    'middle' : B('\[','\]'),
    'middle-1' : B('〔', '〕'),
    'big' : B('{', '}'),
    'sickle' : B('「', '」'),
    'double_sickle' : B('『','』'),
    'double_inequal' : B('《', '》')
    }

unify_dict = {
    'quotation' : Rx('[“”]', '"', 1),
    'apostrophe' : Rx('[‘’]', "'", 1),
    'middle' : Rx('[ㆍㆍ]', ',', 1),
    'hyphen' : Rx('[─ㅡ⎯―\—]', '-', 1),
    'ellipsis' : Rx('\.\.\.+|‥+|…', '⋯', 1)
}

default_dict = {
    'wrong_bracket' : Rx('&lt;|&gt;', '', 100)
}

end_marks = '[\].\?!]'
