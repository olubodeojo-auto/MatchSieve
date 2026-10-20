import unittest
from unittest.mock import patch
from matchsieve.ollama_client import OllamaClient

class OllamaClientTests(unittest.TestCase):
    @patch('matchsieve.ollama_client.urllib.request.urlopen')
    def test_ollama_client_posts_only_given_evidence(self,mock_urlopen):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*a): pass
            def read(self): return b'{"message":{"content":"The evidence is limited."}}'
        mock_urlopen.return_value=Response()
        client=OllamaClient(base_url='http://127.0.0.1:11434',model='unit-test',timeout=1)
        text=client.write_commentary({'fixture':{'home_team':'A','away_team':'B'},'market':{'label':'Under 4.5'},'status':'LIMITED_EVIDENCE','missing_information':['line-ups not supplied']})
        self.assertEqual(text,'The evidence is limited.')
        args,kwargs=mock_urlopen.call_args
        self.assertIn('/api/chat',args[0].full_url)
        self.assertNotIn('API_KEY',args[0].data.decode())

if __name__=='__main__': unittest.main()
