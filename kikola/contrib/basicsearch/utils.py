def load_cls(name):
    module_name, cls_name = name.rsplit('.', 1)

    module = __import__(module_name)
    parts = module_name.split('.')

    for part in parts[1:]:
        module = getattr(module, part)

    return getattr(module, cls_name)
