import os
virtenv = os.path.join(os.environ.get('OPENSHIFT_PYTHON_DIR','.'), 'virtenv')

from demo import *

if __name__ == '__main__':
    main()
