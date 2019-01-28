import requests

def html(domain):
	req = requests.get(domain)
	return req.text


def find(s, s_key, e_key):
	s_idx = s.find(s_key)
	if s_idx >= 0:
		s_idx += len(s_key)
		e_idx = s[s_idx:].find(e_key)
		if e_idx > 0:
			return s[s_idx:s_idx+e_idx]
	return ''