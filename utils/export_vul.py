# coding:utf-8
import pickle

"""
用于导出一条漏洞信息
"""


def store_data():
    vuls = {
    "公开日期" : "2019-05-16",
    "验证信息" : "(暂无验证信息)",
    "漏洞解决方案" : "厂商已发布了漏洞修复程序，请及时关注更新：\r\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\thttps://www.myomron.com/index.php?action=kb&article=1711",
    "更新时间" : 1557964800000.0,
    "CNVD-ID" : "CNVD-2019-14546",
    "title" : "Omron CCX-Supervisor类型混淆漏洞",
    "漏洞类型" : "通用型漏洞",
    "厂商补丁" : "Omron CX-Supervisor类型混淆漏洞的补丁",
    "参考链接" : "https://ics-cert.us-cert.gov/advisories/ICSA-19-017-01",
    "CVE ID" : "CVE-2018-19019",
    "影响产品" : "OMRON CX-Supervisor <=3.42",
    "score" : "6.8",
    "漏洞描述" : "Omron CX-Supervisor是一个功能强大且先进的机器可视化软件包，提供一个非常灵活的基于PC的HMI环境。\n\r\n\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\tOmron CX-Supervisor 3.42及更早版本存在类型混淆漏洞，攻击者可通过特制项目文件利用该漏洞以应用程序权限执行代码。",
    "收录时间" : "2019-05-16",
    "报送时间" : "2019-01-18",
    "危害级别" : "中\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\t\t\t\t\t\t(AV:N/AC:M/Au:N/C:P/I:P/A:P)",
    "漏洞附件" : "(无附件)"
}
    db_file = open('../omron.vul', 'ab')
    pickle.dump(vuls, db_file)
    db_file.close()


if __name__ == '__main__':
    store_data()