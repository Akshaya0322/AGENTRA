import langchain, pkgutil, sys, importlib
print('langchain version', getattr(langchain, '__version__', 'unknown'))
print('langchain path', langchain.__path__)
mods = [m.name for m in pkgutil.iter_modules(langchain.__path__)]
print('submodules list:', mods)
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print('import RecursiveCharacterTextSplitter OK')
except Exception as e:
    print('Import error:', e)
