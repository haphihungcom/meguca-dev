def dar(tag_name, value, options, parent, context):
    return "[abc]{}[/abc]".format(value)


def foo(tag_name, value, options, parent, context):
    return "[efg={}]{}[/efg]".format(context['custom_vars']['key1'], value)


def bar(tag_name, value, options, parent, context):
    return "[xyz={}]{}[/xyz]".format(context['config']['conf1'], value)


def moo(tag_name, value, options, parent, context):
    return "[vnm={}]{}[/vnm]".format(options['moo'], value)