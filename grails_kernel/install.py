# Taken from https://github.com/takluyver/bash_kernel/blob/master/bash_kernel/install.py
import json
import os
import sys
import getopt

from jupyter_client.kernelspec import KernelSpecManager
from IPython.utils.tempdir import TemporaryDirectory

kernel_json = {
    "argv": [sys.executable, "-m", "grails_kernel", "-f", "{connection_file}"],
    "display_name": "Grails",
    "language": "groovy",
    "codemirror_mode": "groovy",
}


def install_my_kernel_spec(user=True, prefix=None):
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755) # Starts off as 700, not user readable
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)
        # TODO: Copy resources once they're specified

        print('Installing IPython kernel spec')
        KernelSpecManager().install_kernel_spec(td, 'grails', user=user, replace=True, prefix=prefix)


def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False # assume not an admin on non-Unix platforms


def main(argv=[]):
    prefix = None
    user = not _is_root()

    opts, _ = getopt.getopt(argv[1:], '', ['user', 'prefix='])
    for k, v in opts:
        if k == '--user':
            user = True
        elif k == '--prefix':
            prefix = v
            user = False

    install_my_kernel_spec(user=user, prefix=prefix)

if __name__ == '__main__':
    main(argv=sys.argv)
