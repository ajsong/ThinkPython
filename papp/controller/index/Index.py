# -*- coding: UTF-8 -*-
from .Core import *
from ...model.Member import *


class Index(Core):

    def index(self):
        for g in (res := Member.alias('m')
                .leftJoin('member p', 'p.id=m.parent_id')
                .field('m.id, m.wallet, p.wallet as parent, m.reg_time')
                .limit(10).select()):
            g['reg_time'] = date('%Y-%m-%d %H:%M', g['reg_time'])
        return self.render({
            'list': res
        })
