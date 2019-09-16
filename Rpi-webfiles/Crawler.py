import requests


def html(domain):
    req = requests.get(domain)
    return req.text


def find(s, s_key, e_key='', idx=0):
    s_idx = s.find(s_key)
    i = 0
    while i < idx:
        m = s[s_idx+1:]
        n = m.find(s_key)
        if n > 0:
            s_idx += n + 1
        else:
            s_idx = -1
        i = i + 1
    if s_idx >= 0:
        s_idx += len(s_key)
        e_idx = -1
        if len(e_key) > 0:
            e_idx = s[s_idx:].find(e_key)
        if e_idx > 0:
            return s[s_idx:s_idx + e_idx]
        else:
            return s[s_idx:e_idx]
    return ''


if __name__ == '__main__':
    s = html('https://www.wunderground.com/weather/br/macau?bannertypeclick=htmlSticker&GO=SEARCH')
    a = find(s, '<span _ngcontent-c12="" class="wx-value">', '</span>', idx=0)
    print(a)
