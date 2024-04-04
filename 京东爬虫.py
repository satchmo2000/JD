#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time   : 2024/4/4

import requests
from bs4 import BeautifulSoup
import xlwt
import time
from urllib.parse import quote

# 保存页面参数（仅第一次保存，用于参数选择的参考）
para_showfirst = True
para_listfirst = []

PARAMETER_LABEL_DEFAULT = ['商品毛重', '商品产地', '功效', '适用发质', '总净含量', '适合头皮', '评论数']

# 发送访问请问的head文件
# 每个电脑每个京东账号对应的head文件不同，获取方式参考帖子https://blog.csdn.net/weixin_41998772/article/details/106476166
# 经试验，只要把cookie、user-agent更新一下即可（其中cookie会变）
# 按下F12（以火狐为例）
# 打开https://search.jd.com/Search?keyword=洗发水&qrst=1&wq=洗发水&stock=1&page=1&s=1&click=1
# 进入网络页面的第一条，显示域名为“search.jd.com”，右键“复制值/复制为cUrl命令（POSIX）”
# 复制'Cookie:...'引号内，冒号后面的内容，并替换到下面cookie的值
# 同样复制'User-Agent:...'引号内，冒号后面的内容，并替换下面user-agent后面的值

cookie = 'TrackID=1-Ju0CQPuz_3Egmks_HSbCP_tLXKa-o43Emlm9y6aq15INjdrjzR7Jf3scxZ1ot6rI-viHUf0PW1o9qumPdvY5-EEUb7GF-k8mmYpRtkW_mwXc66_H4EV4uuEvbvyeAbi; shshshfp=36d907cf7ac8caf010da0eaccc807b26; shshshfpa=a84f18a9-2bfd-655d-b6c8-095232d37d4a-1532838024; shshshfpb=BApXeAYHuoutAuba52bqL6QQBYCWJFcyQBHDChwtX9xJ1MmQogIO2; __jda=143920055.17047929986231674504267.1704792999.1712049752.1712112447.26; __jdu=17047929986231674504267; 3AB9D23F7A4B3CSS=jdd03HYA5SJEK3TGHVOYNAPCHD2YPPDBBUJCTQB3XR4DIM77J55WOMZ6Z2EQ5M4DYTFYIBIM4RPGM3ZT4ONA7Y5HILHKFDEAAAAMOUHSLELYAAAAACHHPWY654WTC4EX; shshshfpx=a84f18a9-2bfd-655d-b6c8-095232d37d4a-1532838024; ipLoc-djd=1-2800-0-0; pinId=nE0Vz3xk1DpSoTbTtmr-Sg; pin=satchmo2000; unick=satchmo2000; _tp=7k8aaz3rMoAM3T^%^2FM9DJdtQ^%^3D^%^3D; _pst=satchmo2000; xapieid=jdd03HYA5SJEK3TGHVOYNAPCHD2YPPDBBUJCTQB3XR4DIM77J55WOMZ6Z2EQ5M4DYTFYIBIM4RPGM3ZT4ONA7Y5HILHKFDEAAAAMOUHSLELYAAAAACHHPWY654WTC4EX; qrsc=3; ipLocation=^%^u5317^%^u4eac; cn=34; user-key=6c7c5a43-e18a-4e3e-ad3b-c00b91041dc6; __jdv=76161171^|direct^|-^|none^|-^|1711094373638; PCSYCityID=CN_110000_110100_0; thor=44BA6D32ADC8C20B5A3C3D13EFC07B00EDFCAE2194F9DE0F7ACF2C420E982102A36C6FF412C7E7B2F9202F74ADE82078A70E37F75C0941B53F8A7CE36F20203A8A232AE067C2206D12CB14C1A481BE9C93B766537484FB0BF21A4A32D5DA2F1C337342FF642B2B921EB39BE0D81DE864B5161F63D423D5A827DBF5EC1DDF831FFEB7A8DE18B7FE5B55B3E2B4B9E8AA2D; flash=2_iDK3zBrrfYJrkzetcZ8oTlkTWchEwSmXBQCGhXwANe7dBIfxHl_m3JZkmojo6boSTfB1BTnvqg7cwPu0alp1Bl023ris_ZvDMA-_PWylqvL*; areaId=1; __jdb=143920055.7.17047929986231674504267^|26.1712112447; __jdc=143920055; source=PC; platform=pc; jsavif=1; jsavif=1; rkv=1.0; avif=1; 3AB9D23F7A4B3C9B=HYA5SJEK3TGHVOYNAPCHD2YPPDBBUJCTQB3XR4DIM77J55WOMZ6Z2EQ5M4DYTFYIBIM4RPGM3ZT4ONA7Y5HILHKFDE'

# 搜索关键字（并转成UTF8格式）
key = str(input('请输入需要爬取的信息关键字：'))
total = input('请输入需要爬取页数: ')

key = quote(key)

#url_def = f"https://search.jd.com/Search?keyword={key}&qrst=1&wq={key}&stock=1&page=1&s=1&click=1"

headers_def = {  
    'cookie': cookie,
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
}

def is_https_string(s):
    return s.startswith("https")

def is_showfirst():
    global para_showfirst
    showfirst = para_showfirst
    para_showfirst = False
    return showfirst

class Config():
    '''
    PARAMETER_LABEL：需要根据爬取的商品详情界面的信息key进行修改，其中'评论数'是另一种方式获取的
    TITLE_LABEL：PARAMETER_LABEL修改后excel的表头也做相应的修改
    GOOD_LABEL：无需修改，默认该四个信息都爬取
    need_list：能直接从html解析后的标签文件中获取的
    '''
    
    global PARAMETER_LABEL_DEFAULT
    
    # excel表头
    TITLE_LABEL = ['商品名称', '价格', '商家', '商品详情地址'] + PARAMETER_LABEL_DEFAULT
    print('title_label=', TITLE_LABEL)
    # html中对应TITLE_LABEL的key
    GOOD_LABEL = ['name', 'price', 'shop', 'detail_addr']
    # TITLE_LABEL中商品详情页（即点进单个商品界面）想爬取的数据在html中key，'评论数'一定要放在最后
    PARAMETER_LABEL = PARAMETER_LABEL_DEFAULT
    print('parameter_label=', PARAMETER_LABEL)
    # 将PARAMETER_LABEL去掉'评论数'即为need_list
    need_list = PARAMETER_LABEL[:-1]
    # 将搜索页的key和单个商品详情页的key组合起来
    TOTAL_LABEL = GOOD_LABEL + PARAMETER_LABEL
    # excel文件的保存路径
    SAVE_PATH = './test.xls'

    headers = {
        'cookie': '_jda=143920055.377758356.1573641686.1712151977.1712156679.604; __jdu=377758356; shshshfp=aec0269da7f1e4827b534e76910e7df8; shshshfpa=22f7b497-92e9-3621-9ba7-7fd8f825e3f2-1573641728; shshshfpb=BApXeHKp3p-tAARqHYK7YlSluFq9D41IoBDElEAdX9xJ1MuHmvIO2; pinId=nE0Vz3xk1DpSoTbTtmr-Sg; TrackID=1IPl_g-SJ0yP5rntayJgTS53cWzsuWtxaH9bhItIgHLebMWWbg3_6jAB2567u6f-L0jqS1Df8wCl66j8g0WiaWagOWSDh2bodrhcRpWrtLyi-D8SzbdNTi0aB8a9Ch3Tn; shshshfpx=22f7b497-92e9-3621-9ba7-7fd8f825e3f2-1573641728; 3AB9D23F7A4B3CSS=jdd03AJ3KTT467STM3U7QH2XA2UICI4JLU4J6DHHZJ5MVWF2R3IDV4RSNV33WOH6X5QMK6YSLDIH35B4DJKI62MTTGZFZ5YAAAAMOUR64MTQAAAAACV46MVDVESLE7QX; xapieid=jdd03AJ3KTT467STM3U7QH2XA2UICI4JLU4J6DHHZJ5MVWF2R3IDV4RSNV33WOH6X5QMK6YSLDIH35B4DJKI62MTTGZFZ5YAAAAMOUR64MTQAAAAACV46MVDVESLE7QX; ipLoc-djd=1-2810-55541-0.683374302; pin=satchmo2000; unick=satchmo2000; _tp=7k8aaz3rMoAM3T%2FM9DJdtQ%3D%3D; _pst=satchmo2000; ipLocation=%u5317%u4eac; qrsc=3; cn=26; areaId=1; __jdv=76161171|direct|-|none|-|1711972011679; PCSYCityID=CN_110000_110100_0; thor=44BA6D32ADC8C20B5A3C3D13EFC07B00EDFCAE2194F9DE0F7ACF2C420E982102CFA124FFF8445CA6A11E313EB029BF4E9B6581C81A0C9A9A3956EE73861EA6E41746123EE5A6D6FE0C55ACA6962738C31C474765FC491148DAC94CD58C7AE7CA5BF2390D48A9B16031B82B645FA47DFF28C8751541134E2678A28BC1E8479DF1C21C285FDF596BEDAD58DC2C6BD8EA53; flash=2_tAZBFdnOn3NAnsEu6y7gQ8Xo_G0QgfDBUs1paetY1TXr4SfkmL9M3n3ygICFBsvMo-iN36R-G7-9gVCXpi4eCBVzOd8FPy6HqKHNxKkfZ7V*; __jdc=143920055; __jdb=143920055.4.377758356|604.1712156679; mba_muid=377758356; mba_sid=17121566795924738356974954310.1; __jd_ref_cls=LoginDisposition_Go; x-rp-evtoken=N-nAb5Oj6OS1u8hkvixIgJrl8LLGlf_PLuo79iC-d0OQ4zCbf1fNCBrsmRFHp7VvrVanas_IWr_E1hgJviTIGd4CeDFCa1fQT8pqFxUcBx07nn4dbjAjJ4Mad7vZ8Ph9CtZ0OM4SJ8bDVna3O0m2quGv23FkFEubjtChkDeEvq9OIt6e2pa65Sj1JZnFo5SiVBYS-oGOwwrB9K06u-1mn4OdnBustb73yaebATpBzxY%3D; token=0695b5fa9c7ee0985a74508d835dafb8,3,951198; __tk=5cdb7abb7a337cbcf6cb865fd02039e7,3,951198; jsavif=1; _gia_d=1; avif=1; jsavif=1; rkv=1.0; 3AB9D23F7A4B3C9B=AJ3KTT467STM3U7QH2XA2UICI4JLU4J6DHHZJ5MVWF2R3IDV4RSNV33WOH6X5QMK6YSLDIH35B4DJKI62MTTGZFZ5Y',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    }
    global key
    global total
    global headers_def
    
    keyword = key
    totalpage = total
    headers = headers_def

class Excel():
    # 表格列数
    TABLE_COL = len(Config.TITLE_LABEL)
    # 当前行数
    _current_row = 1

    # 初始化，创建文件及写入title
    def __init__(self, sheet_name='sheet1'):
        self.write_work = xlwt.Workbook(encoding='ascii')
        self.write_sheet = self.write_work.add_sheet(sheet_name)
        for item in range(len(Config.TITLE_LABEL)):
            # 第一行写入excel表头
            self.write_sheet.write(0, item, label=Config.TITLE_LABEL[item])

    # 写入内容
    def write_content(self, content):
        try:
            #print(content)
            if content['detail_addr'] != '无':  # 有时候没能获取的该商品的详情地址就跳过该商品
                for item in range(self.TABLE_COL):
                    if (item == self.TABLE_COL - 1) and (Config.TOTAL_LABEL[-1] == '标题材质关键字'):
                        self.write_sheet.write(self._current_row, item, label=self.title_extract(content['name']))
                    else:
                        self.write_sheet.write(self._current_row, item, label=content[Config.TOTAL_LABEL[item]])
                # 插入完一条记录后，换行
                self._current_row += 1
        except Exception as e:
            print('write_content error,', e)

    # 保存文件
    def save_file(self, file_url=Config.SAVE_PATH):
        try:
            self.write_work.save(file_url)
            print("文件保存成功！文件路径为：" + file_url)
        except IOError:
            print("save_file,文件保存失败！")

    # 提取商品标题中的材质关键词
    def title_extract(self, title):
        # 想要提取的关键词列表
        materials = ['陶瓷', '骨瓷', '玻璃', '搪瓷', '木制', '木质', '不锈钢', '塑料']
        contain = ''
        count = 0
        for material in materials:
            if material in title:
                # 将最后的输入形式为 “陶瓷、木质、不锈钢”
                if count == 0:
                    contain = contain + material
                    count += 1
                else:
                    contain = contain + '、' + material
                    count += 1
        return contain

class Goods:
    # 初始化方法
    def __init__(self, li_info,page,row):
        self.pageId = page
        self.rowId = row
        self.li_info = li_info
        self.good_info_dic = {}

    def acquire_comment(self, url):
        try:
            '''
            input:
                url：商品详情地址(detail_addr)，形式如//item.jd.com/100007046969.html
            rerurn:
                comment_count：该商品的评论数,现在能爬取到的都是大约数，比如“2万+”,详细的评论总数京东暂时没显示在html信息中（2021.08.03）
            '''
            # 提取商品详情地址中的商品号
            no = url.split('com/')[1].split('.html')[0]
            comment_url = "https://club.jd.com/comment/productPageComments.action?callback1=fetchJSON_comment98&productId=" + no + "&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1"
            #comment_url = "http:" + url + '#comment'
            print("评论数获取链接：", comment_url)
            response = requests.get(comment_url, headers=Config.headers)
            #time.sleep(2)
            
            page = response.content.decode('utf-8')  # type(page)为str，fetchJSON_comment98(dic),dic['productCommentSummary']['commentCountStr']为评论数
            # "commentCountStr":"2万+", 获取其中的2万+，暂时想到的办法是用split和replace对字符串进行切分后再替换不需要的字符
            
            comment_count = page.split("commentCountStr")[1].split(':')[1].split(',')[0].replace('"', '')
            return comment_count
        except Exception as e:
            print('acquire_comment error', e)
            
    def add_product_parameter(self, need_list, url):
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        #time.sleep(2)
        # 获取商品参数
        parameters = soup.find('ul', class_='parameter2 p-parameter-list')
        para_lists = parameters.find_all('li')
        #print(parameters)
        #print(para_lists)
        print('para count=', len(para_lists))
        name_lists = []
        para_text_lists = []
        for para in para_lists:
            para_text = para.get_text().split("：")
            #print(para_text)
            # para_text的形式：“商品名称：浩雅HY160”
            name_lists.append(para_text[0])  # name_lists保存单个商品详情页参数名称，如“商品名称”
            para_text_lists.append(para_text[1])  # para_text_lists保存参数名称对应的参数，如”浩雅HY160“

        if is_showfirst():
            global para_listfirst
            para_listfirst = name_lists.copy()

        return_list = []
        # 按need_list中参数名称的顺序保存单个商品详情页中的爬虫数据
        for need in need_list[:-1]:  # 评论数单独拎出来，need_list[-1]为“评论数”
            try:
                index = name_lists.index(need)
                return_list.append(para_text_lists[index])
            except:
                # 如果该商品商家并没有显示该参数名称的参数，那么excel中填充空值
                return_list.append(' ')
        # 最后一列填充评论数
        return_list.append(self.acquire_comment(url))
        return return_list

    def find_attr(self, attr):
        try:
            if attr == Config.GOOD_LABEL[0]:
                # 商品名称
                result = self.li_info.find(class_='p-name p-name-type-2').find('em').get_text()
            elif attr == Config.GOOD_LABEL[1]:
                # 价格
                result = self.li_info.find(class_='p-price').find('i').get_text()
            elif attr == Config.GOOD_LABEL[2]:
                # 商家
                result = self.li_info.find(class_='p-shop').find('a').get_text()
            elif attr == Config.GOOD_LABEL[3]:
                # 商品详情地址
                result = self.li_info.find(class_='p-name p-name-type-2').find('a')['href']
                if not is_https_string(result):
                    result = f'https:{result}'
                print('page = ', self.pageId, 'row = ', self.rowId, 'url = ', result)

                # 进入单个商品详情网页进行数据爬取，本代码所说的单个商品详情网页意思为从搜索页点进某一个商品页，比如https://item.jd.com/100007046969.html
                paras = self.add_product_parameter(Config.PARAMETER_LABEL, result)
                
                for i in range(len(paras)):
                    para = paras[i]
                    self.good_info_dic.setdefault(Config.PARAMETER_LABEL[i], para)

        except AttributeError:
            result = '无'
        self.good_info_dic.setdefault(attr, result)  # 集合setdefault

    # 添加商品信息
    def add_good_info(self):
        for item in Config.GOOD_LABEL:
            self.find_attr(item)

    # 获取产品列表
    def get_good(self):
        return self.good_info_dic

def get_html(url, currentPage=None, pageSize=None):
    if pageSize:
        print("--> 正在获取网站第 " + str(currentPage) + "页信息")
        if currentPage != 1:
            url = url + '&page=' + str(currentPage) + '&s=' + str(pageSize) + '&click=0'

    #print('get_html=', url)
    response = requests.get(url, headers=Config.headers)  # 请求访问网站
    #time.sleep(2)
    if response.status_code == 200:
        html = response.text  # 获取网页源码
        return html  # 返回网页源码
    else:
        print("获取网站信息失败！")

if __name__ == '__main__':
    '''
    一定需要修改的是Config中的headers文件，每个电脑每个京东账号对应的文件不同
    修改完headers后可以输入关键词为“餐具碗”，页数“2”，查看下爬虫结果
    可根据自己的需求修改Config中的参数
    '''
    # 创建文件
    excel = Excel()

    config = Config()
    # 搜索地址
    search_url = f'https://search.jd.com/Search?keyword={config.keyword}&enc=utf-8&psort=3'
    print('search_url=', search_url)
    page = {
        'total': 0,  # 总页数
        'currentPage': 1,  # 当前页数
        'pageSize': 0  # 每页显示多少条
    }

    if not config.totalpage.isdigit():
        print("非法字符，程序退出！")
        exit(0)

    page['total'] = eval(config.totalpage)
    for i in range(page['total']):
        # 初始化BeautifulSoup库,并设置解析器
        soup = BeautifulSoup(get_html(search_url, page['currentPage'], page['currentPage'] * page['pageSize']), 'lxml')
        print('soup length=', len(soup))
        
        # 商品列表
        goods_list = soup.find_all('li', class_='gl-item')
        print("分析到第" + str(page['currentPage']) + '页共有' + str(len(goods_list)) + '条商品信息')
        rowId = 0
        for li in goods_list:  # 遍历父节点
            time.sleep(2)  # 为了防止爬取太快被京东服务器拦截，在每次解析网页操作后强制休息2秒
            rowId = rowId + 1
            #print(li)
            try:
                goods = Goods(li,i + 1,rowId)
                #print('添加信息')
                goods.add_good_info()
                #print('获取信息')
                good_info = goods.get_good()
                #print('写入excel')
                excel.write_content(good_info)
            except:
                print("商品信息获取失败")
                break

        page['currentPage'] = page['currentPage'] + 1
        page['pageSize'] = len(goods_list) * page['currentPage']

    # 保存excel文件
    excel.save_file(config.SAVE_PATH)