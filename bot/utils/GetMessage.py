from jinja2 import Environment, PackageLoader, select_autoescape


def get_mes(path: str, **kwargs):
    env = Environment(
        loader=PackageLoader(package_name='__main__', package_path="", encoding="utf-8"),
        autoescape=select_autoescape(['html', 'xml'])
    )
    tmpl = env.get_template(path)
    return tmpl.render(kwargs)

