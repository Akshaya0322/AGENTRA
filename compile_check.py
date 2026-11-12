import compileall, pathlib, sys
root = pathlib.Path(r"C:/Users/ADMIN/.gemini/antigravity/scratch/AGENTRA")
result = compileall.compile_dir(str(root), force=True, quiet=1)
print('Compile result:', result)
