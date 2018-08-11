#这个文件是帮助生成模块导出的，这个模块文件太多了，不方便写

from os.path import dirname, basename, isfile,join
import glob


modules = glob.glob(dirname(__file__)+"/*.py")
lst = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py') and not f.endswith('__help__.py')]

print('开始生成导出信息')

dstFile = join(dirname(__file__), '__init__.py');
with open(dstFile, mode='w', encoding='utf-8') as op:
    op.write('#自动生成的文件，修改会被覆盖\n')
    for item in lst:
        op.write('from .%s import %s\n'%(item, item))

    op.write('\n\n\n')

    op.write('__all__ = [\n')
    for item in lst:
        op.write('\t\t%s,\n'%(item,))
    op.write(']\n')

    op.flush()


