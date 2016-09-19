from grails_kernel.kernel import GrailsKernel
from ipykernel.kernelapp import IPKernelApp
if __name__ == '__main__':
    IPKernelApp.launch_instance(kernel_class=GrailsKernel)
