from meguca.plugins.src.dispatch_updater import BBCode


@BBCode.register('dar')
class Dar():
    def format(self, tag_name, value, options, parent, context):
        return "[abc]{}[/abc]".format(value)


@BBCode.register('foo', render_embedded=False)
class Foo():
    def format(self, tag_name, value, options, parent, context):
        return "[efg={}]{}[/efg]".format(context['example']['hoo'], value)


@BBCode.register('bar')
class Bar():
    def format(self, tag_name, value, options, parent, context):
        return "[xyz={}]{}[/xyz]".format(self.config['testkey'], value)


@BBCode.register('moo')
class Moo():
    def format(self, tag_name, value, options, parent, context):
        return "[vnm={}]{}[/vnm]".format(options['moo'], value)