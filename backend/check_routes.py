import sys
sys.path.insert(0, '..')

from app.main import app
print(f"Total routes: {len(list(app.routes))}")
for route in app.routes:
    print(f'  type={type(route).__name__}', end='')
    if hasattr(route, 'path'):
        print(f' path={route.path}', end='')
    if hasattr(route, 'methods'):
        print(f' methods={route.methods}', end='')
    if hasattr(route, 'name'):
        print(f' name={route.name}', end='')
    print()
