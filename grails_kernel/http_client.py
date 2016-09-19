try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
from slimit.lexer import Lexer
from requests import Session
import logging

logger = logging.getLogger(__name__)


class GrailsConsoleClient:

    def __init__(self):
        self._session = Session()
        self._html_parser = HTMLParser()
        self._js_lexer = Lexer()
        self._remote_url = 'http://localhost:8080/testapp'
        self.authenticated = False

    def _normalize_output(self, console_output):
        lines = [line for line in console_output.split('<br/>') if line and not line.startswith('groovy&gt;')]
        response = '\n'.join(lines)
        return self._html_parser.unescape(response)

    def execute(self, grails_code):
        """
        Return result, output, exception of executed grails_code, accepting a str:
        >>> self.execute("1 + 1")
        ('2', '', '')
        """
        res = self._session.post('%s/console/execute' % self._remote_url, data={
            'code': grails_code,
            'captureStdout': 'true'
        })
        res = res.json()
        result = self._normalize_output(res['result'])
        output = self._normalize_output(res['output'])
        exception = self._normalize_output(res['exception']['stackTrace']) if 'exception' in res else ''
        return result, output, exception

    def authenticate_without_spring_security(self):
        from lxml import html
        response = self._session.get('%s/console' % self._remote_url)
        tree = html.fromstring(response.content)
        self._js_lexer.input(tree.xpath('//script[contains(.,"App")]')[0].text)

        for token in self._js_lexer:
            if token.type == 'STRING' and '"csrfToken"' in token.value:
                assert self._js_lexer.token().value == ':'
                csrf = self._js_lexer.token().value[1:-1]
                break
        else:
            raise ValueError()
        self._session.headers['X-CSRFToken'] = csrf
        self.authenticated = True

    def authenticate_with_spring_security(self, url, username, password):
        previous = self._remote_url
        self._remote_url = url
        try:
            response = self._session.post(
                '%s/api/login' % self._remote_url,
                allow_redirects=False,
                json={
                    'username': username,
                    'password': password,
                },
            )
            try:
                data = response.json()
                access_token = data['access_token']
            except Exception as e:
                logger.error('Problem logging in: %s\n' % response.text)
                raise e
            self._session.headers['Authorization'] = 'Bearer {0}'.format(access_token)
            response = self._session.post(
                '%s/j_spring_security_check' % self._remote_url,
                params={
                    'j_username': username,
                    'j_password': password,
                    '_spring_security_remember_me': 'on',
                }, allow_redirects=False
            )
            assert 'authfail' not in response.headers['location'], \
                "Failed to login %s" % response.headers['location']
            self.authenticated = True
        except:
            self._remote_url = previous
            raise


