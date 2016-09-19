from grails_kernel.http_client import GrailsConsoleClient
from ipykernel.kernelbase import Kernel
import shlex
import json

REMOTE_USAGE = """\
UsageError: Please provide these arguments: URL USERNAME PASSWORD
    Where URL is the url for a grails application using the grails console plugin.
    Example:
      %%remote https://example.com me@gmail.com PaS5w0rD!
"""


class GrailsKernel(Kernel):

    implementation = 'Grails'
    implementation_version = '1.0'
    language = 'groovy'
    language_version = '0.1'
    language_info = {
        'name': 'groovy',
        'file_extension': 'groovy',
        'mimetype': 'text/x-groovy'
    }
    banner = "Grails Kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._console = GrailsConsoleClient()
        # try:
        #     self._console.authenticate_without_spring_security()
        # except ValueError:  # TODO
        #     pass

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            if not silent:

                code_lines = code.split('\n')

                if code_lines and len(code_lines[0]) >= 8 and code[:8].lower() == '%%remote':
                    args = shlex.split(code_lines[0])

                    if len(args) < 4:
                        self.send_response(self.iopub_socket, 'stream', {
                            'name': 'stdout', 'text': REMOTE_USAGE
                        })
                        return {
                            'status': 'error',
                            'execution_count': self.execution_count,
                            'payload': [],
                            'user_expressions': {},
                        }

                    try:
                        self._console.authenticate_with_spring_security(*args[1:])
                    except Exception as e:
                        self.send_response(self.iopub_socket, 'stream', {
                            'name': 'stderr', 'text': '%s: %s' % (e.__class__.__name__, str(e.args))
                        })
                else:

                    result, output, exception = self._console.execute(code)

                    if output:
                        self.send_response(self.iopub_socket, 'stream', {
                            'name': 'stdout', 'text': '%s\n' % output})

                    if exception:
                        self.send_response(self.iopub_socket, 'stream', {
                            'name': 'stderr', 'text': exception})
                    if result:
                        self.send_response(self.iopub_socket, 'stream', {
                            'name': 'stdout', 'text': result})

            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }

        except Exception as e:
            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stderr', 'text': '%s: %s' % (e.__class__.__name__, str(e.args))})
            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }

    def do_complete(self, code, cursor_pos):
        matches = []

        default = {
            'matches': [], 'cursor_start': cursor_pos,
            'cursor_end': cursor_pos, 'metadata': dict(),
            'status': 'ok'
        }

        if not code:
            return default

        if code[cursor_pos-2] in (' ', '\n'):
            matches += [
                "session",
                "request",
                "ctx",
                "grailsApplication",
                "config",
                "log",
                "out",
                'import',
                'println',
                'def',
                'for',
                'instanceof',
                'new',
                'null',
                'true',
                'false',
            ]

            # matches += json.loads(self._console.execute("""\
            # import groovy.json.*
            # def json = new groovy.json.JsonBuilder()
            # json {response this.binding.variables.keySet()}
            # json.toString()
            # """)[0])

        elif code[cursor_pos-2] == '.':
            pass  # TODO complete for types via: http://groovy-almanac.org/list-the-methods-of-a-groovy-class/

        return {
            'matches': sorted(matches),
            'cursor_start': 0,
            'cursor_end': cursor_pos,
            'metadata': dict(),
            'status': 'ok'
        }

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        """DEPRECATED"""
        raise NotImplementedError

    def do_clear(self):
        """DEPRECATED"""
        raise NotImplementedError
