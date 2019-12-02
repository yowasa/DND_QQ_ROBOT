from filter import msg_route
from tool.spell_db import *
import re

'''
法术速查功能
.spell <法术名> [level:<环数>] [job:<职业>] 法术速查

'''

SPELL_PATTERN = re.compile(r'\s*(?P<command>\.\w+)(?P<args>.*)', flags=re.M | re.S)
SPELL_ARG_PATTERN = re.compile(r'(?P<key>\w+)[:：]\s*(?P<quote>")?(?P<value>(?(quote)[^"]+|\S+))(?(quote)")', flags=re.M)
LEVEL_PATTERN = re.compile(r'(?P<level>\d+)\s*环?')


def format_one_spell(s):
    return '\n'.join([
        '%s %s' % (s.name, s.ename),
        '%s环 %s' % (s.level, s.type),
        '施法时间: %s' % s.cast_time,
        '施法距离: %s' % s.cast_range,
        '法术成分: %s' % s.component,
        '持续时间: %s' % s.duration,
        s.describe
    ])


def gen_one_spell_msg(s):
    spell_str = format_one_spell(s)
    rel_jobs = ', '.join(('%s %s' % (js.job.name, js.job.ename) for js in s.jobs))
    if spell_str[-1] == '\n':
        spell_str = '%s* 相关职业：%s' % (spell_str, rel_jobs)
    else:
        spell_str = '%s\n* 相关职业：%s' % (spell_str, rel_jobs)
    return spell_str


SPELL_HANDLER_HELP_MSG = \
    '''
    .spell <法术名> [level:<环数>] [job:<职业>] 
    用于查询法术
    当有多个结果时，输出名称列表;
    当仅一个结果时，输出法术详细信息。
    注：.spell job:list 会列出具有法术的职业。
    '''


# 查询技能
@msg_route(r'\s*\.spell')
def spell_handler(context):
    cmd_m = SPELL_PATTERN.match(context['message'])
    if not cmd_m or not cmd_m.group('args').strip():
        return SPELL_HANDLER_HELP_MSG
    args = {}
    for m in SPELL_ARG_PATTERN.finditer(cmd_m.group('args')):
        args[m.group('key')] = m.group('value').strip()
    query_where = None
    name = SPELL_ARG_PATTERN.sub('', cmd_m.group('args')).strip()
    spell = Spell.get_or_none((Spell.name == name) | (Spell.ename == name))
    if spell:
        return gen_one_spell_msg(spell)
    if name:
        name = '%{}%'.format(name)
        query_where = ((Spell.name ** name) | (Spell.ename ** name))

    if 'level' in args:
        try:
            m = LEVEL_PATTERN.search(args['level'])
            if not m: return 'level:%s 未找到' % args['level']
            level = int(m.group('level'))
            if query_where:
                query_where = query_where & (Spell.level == level)
            else:
                query_where = (Spell.level == level)
        except:
            return 'level:%s 未找到' % args['level']

    if 'job' in args:
        if 'list' == args['job']:
            reply = '\n'.join(('%s %s' % (j.name, j.ename) for j in Job.select()))
            return reply
        job_name = '%{}%'.format(args['job'])
        job = Job.get_or_none((Job.name ** job_name) | (Job.ename ** job_name))
        if not job:
            return 'job:%s 未找到' % args['job']
        if query_where:
            query_where = (JobSpell.job == job) & query_where
        else:
            query_where = (JobSpell.job == job)
        query = (Spell
                 .select(Spell.id, Spell.name, Spell.ename, Spell.level)
                 .join(JobSpell)
                 .where(query_where)
                 .order_by(Spell.level, Spell.name, Spell.ename))
        reply_arr = ['%s法术 %s spells' % (job.name, job.ename)]
        cur_level = -1
        cnt = 0
        last_spell = None
        for s in query:
            cnt += 1
            last_spell = s
            if cur_level < s.level:
                reply_arr.append('%s环：' % s.level)
                cur_level = s.level
            reply_arr.append('%s %s' % (s.name, s.ename))
        if cnt == 1:
            reply = gen_one_spell_msg(Spell.get_by_id(last_spell.id))
        else:
            reply = '\n'.join(reply_arr)
        return reply

    query = (Spell
             .select()
             .where(query_where)
             .order_by(Spell.level, Spell.name, Spell.ename))

    spells = [s for s in query]
    if len(spells) > 1:
        reply = '\n'.join(('%s %s' % (s.name, s.ename) for s in spells))
    elif len(spells) == 1:
        reply = gen_one_spell_msg(spells[0])
    else:
        reply = '未找到匹配法术'

    return reply
