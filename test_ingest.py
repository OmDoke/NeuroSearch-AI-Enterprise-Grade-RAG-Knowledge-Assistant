import traceback
from backend.services.embeddings import get_vector_store

try:
    vs = get_vector_store()
    print('VS Init:', vs is not None)
    if vs:
        vs.add_texts(['Hello World'])
        print('Success!')
except Exception as e:
    print('ERROR OCCURRED')
    traceback.print_exc()
