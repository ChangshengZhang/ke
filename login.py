#!/usr/bin/python
# -*- coding: utf-8 -*-
# File Name: login.py
# Author: Changsheng Zhang
# mail: zhangcsxx@gmail.com
# Created Time: Sat Dec 15 14:29:59 2018

#########################################################################

import asyncio
import time
import random
import sys
import datetime
import re
import os
import glob
from pyppeteer.launcher import launch
from exe_js import js1, js3, js4, js5


class Ke():

    def __init__(self, city):
        self.city = city

    async def scroll_by_page(self, page, scroll_index = 1, sleep_time = 1):

        await asyncio.sleep(sleep_time)
        await page.evaluate('window.scrollBy(0, {}*window.innerHeight)'.format(str(scroll_index)))
        await asyncio.sleep(sleep_time)

    async def login(self):

        self.login_url = 'https://sh.ke.com'
        un = '18800111906'
        pwd = 'shbk2018'

        self.browser = await launch({'headless':False})
        self.page = await self.browser.newPage()
        await self.page.goto(self.login_url)
        await asyncio.sleep(2)
        
        await self.page.evaluate(js1)
        await self.page.evaluate(js3)
        await self.page.evaluate(js4)
        await self.page.evaluate(js5)

        await self.scroll_by_page(self.page, 0.5)
        await self.page.querySelectorAllEval('a.btn-login.bounceIn.actLoginBtn', 'el => el[0].click()')
        #await self.page.click('a.btn-login.bounceIn.actLoginBtn')
        await asyncio.sleep(2)
        #await self.scroll_by_page(self.page)
        await self.page.click('a.change_login_type')
        await self.page.type('input.phonenum_input', un, {'delay':50})
        await asyncio.sleep(2)
        await self.page.type('input.password_type.password_input', pwd, {'delay':80})
        await asyncio.sleep(2)
        await self.page.click('div.btn.confirm_btn.login_panel_op.login_submit')
        await self.scroll_by_page(self.page, 0.5, 3)
        
    async def get_xiaoqu_list(self):

        url = 'https://{}.ke.com/xiaoqu/'.format(self.city)
        await self.page.goto(url)
        await self.scroll_by_page(self.page, 0.2, 3)

        position_hder = await self.page.querySelector('div.position')
        position_list = await position_hder.querySelectorAll('a.CLICKDATA')

        position_name_list = []
        position_url_list = []

        for tmp_position in position_list:

            position_url = await self.page.evaluate('(el) => el.href', tmp_position)
            position_name = await self.page.evaluate('(el) => el.innerText', tmp_position)
            
            if position_name == '上海周边' or position_name == '燕郊' or position_name == '香河':
                continue
            if position_url.split('/')[-2] == 'xiaoqu':
                continue

            position_url_list.append(position_url.split('/')[-2])
            position_name_list.append(position_name)
            
        for ii in range(len(position_url_list)):

            if position_url_list[ii] == 'xiaoqu':
                continue
            print(url+position_url_list[ii])
            await self.page.goto(url+position_url_list[ii])
            await self.scroll_by_page(self.page, 0.2, 3)

            if not os.path.exists('./data/xiaoqu/'+self.city+'/'+position_url_list[ii]):
                os.system('mkdir -p data/xiaoqu/'+self.city+'/'+position_url_list[ii])

            sub_position_name_list = []
            sub_position_url_list = []

            position_hder = await self.page.querySelector('div.position')
            sub_position_hder = await position_hder.querySelectorAll('dl')
            sub_position_hder = await sub_position_hder[1].querySelectorAll('div')
            sub_position_list = await sub_position_hder[2].querySelectorAll('a')
            for tmp_sub_position in sub_position_list:

                sub_position_name = await self.page.evaluate('(el) => el.innerText', tmp_sub_position)
                sub_position_url = await self.page.evaluate('(el) => el.href', tmp_sub_position)
                
                sub_position_url_list.append(sub_position_url.split('/')[-2])
                sub_position_name_list.append(sub_position_name)

            for jj in range(len(sub_position_url_list)):

                print(sub_position_url_list[jj])
                if os.path.isfile('./data/xiaoqu/'+self.city+'/'+position_url_list[ii]+'/'+sub_position_url_list[jj]):
                    await asyncio.sleep(3)
                    continue
                f = open('./data/xiaoqu/'+self.city+'/'+position_url_list[ii]+'/'+sub_position_url_list[jj],'w')

                await self.page.goto(url+ sub_position_url_list[jj])
                await self.scroll_by_page(self.page, 0.2, 3)
                tmp_xiaoqu_num = await self.page.querySelectorEval('h2.total.fl','el => el.innerText')
                sub_total_xiaoqu_num = int(re.findall('\d+', tmp_xiaoqu_num)[0])

                for mm in range(int((sub_total_xiaoqu_num - 1)/30) +1):

                    await self.page.goto(url+ sub_position_url_list[jj]+'/pg{}'.format(mm+1))
                    for rr in range(5):
                        await self.scroll_by_page(self.page, 1, 3)

                    sub_xiaoqu_list = await self.page.querySelectorAll('li.clear.xiaoquListItem.CLICKDATA')
                    for tmp_xiaoqu in sub_xiaoqu_list:
                        xiaoqu_title = await tmp_xiaoqu.querySelectorAllEval('div.title', 'el => el[0].innerText')
                        xiaoqu_id = await tmp_xiaoqu.querySelectorAllEval('a.img', 'el => el[0].href')
                        xiaoqu_id = xiaoqu_id.split('/')[-2]
                        print(xiaoqu_id, xiaoqu_title)
                        f.write(xiaoqu_id+','+xiaoqu_title+'\n')

                f.close()
                await asyncio.sleep(random.randint(10,20))
            await asyncio.sleep(random.randint(50,100))

    async def get_ershoufang_list():

        url = 'https://{}.ke.com/xiaoqu/'.format(self.city)
        await self.page.goto(url)
        await self.scroll_by_page(self.page, 0.2, 3)

    async def run(self):

        await self.login()
        await self.get_xiaoqu_list()



async def run():

    city = 'sz'
    a = Ke(city)
    await a.run()



if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
