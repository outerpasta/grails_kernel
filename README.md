A simple untested IPython kernel for a remote [grails-console-plugin](https://grails.org/plugin/console)
enabled application.

To install:

    pip install git+git://github.com/outerpasta/grails-kernel.git
    python -m grails_kernel.install

To use it, run one of:
    
    ipython notebook
    # In the notebook interface, select Grails from the 'New' menu
    ipython qtconsole --kernel grails
    ipython console --kernel grails

You must specify a remote instance of grails, username, and password, for example:

    %%remote https://example.com me@gmail.com password
    
For details of how this works, see the Jupyter docs on wrapper kernels
