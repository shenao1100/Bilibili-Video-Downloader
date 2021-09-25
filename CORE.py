import NTG_base

from lxml import etree
import json
import subprocess
import requests
def GetVidInf(BvId):
    Url = 'https://www.bilibili.com/video/' + BvId
    header = {
        'cookie': '',#Your cookie here
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52',
    }
    result = NTG_base.get(Url, header, '', '')[0]
    tree = etree.HTML(result)
    #视频名称
    VidName = NTG_base.process_file_name(tree.xpath('/html/head/meta[10]/@content')[0])
    VidInf = str(tree.xpath('/html/head/script[5]/text()')[0])
    #格式化为json可以看懂的
    VidInf = VidInf.replace('window.__playinfo__=', '{\"window.__playinfo__\":').replace('\\"', '') + '}'
    VidInf = json.loads(VidInf)['window.__playinfo__']
    #获取链接
    VidLink = VidInf['data']['dash']['video'][0]['baseUrl']
    AduLink = VidInf['data']['dash']['audio'][0]['baseUrl']

    return VidLink, AduLink, VidName

def DownVidAdu(VidLink, AduLink, VidName, path, BvId):
    #keep-alive滞留太多，需要用到session优化
    session = requests.session()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
        'Referer': 'https://www.bilibili.com/' + BvId
    }
    #用options使服务器预分配资源
    session.options(url = VidLink, headers = header, verify=False)
    session.options(url = AduLink, headers = header, verify=False)
    #直到下载完成在跳出循环
    while True:
        result = NTG_base.Download(VidLink, header, path + '\\vid\\' + VidName + '.mp4', session)
        if result == True:
            break
    while True:
        result = NTG_base.Download(AduLink, header, path + '\\adu\\' + VidName + '.mp4', session)
        if result == True:
            break
    #返回保存路径
    return path + '\\vid\\' + VidName + '.mp4', path + '\\adu\\' + VidName + '.mp4'

def ProcessVid(VidPath, AduPath, outputPath, programPath):
    #利用ffmpge合成音视频为一个mp4，也就是最终文件
    cmd = programPath + '\\ffmpeg -i \"' + VidPath + '\" -i \"' + AduPath + '\" -acodec copy -vcodec copy \"' + outputPath + '\"'
    subprocess.call(cmd, shell=True)
    return True


def start():
    a = []#输入bv视频号
    for BvId in a:
        VidLink, AduLink, VidName = GetVidInf(BvId)
        print('获取链接完成 视频名：', VidName)
        tempPath = 'C:\\Users\\NTG\\Desktop\\BilibiliVidDownloader\\temp'#示例
        resultPath = 'C:\\Users\\NTG\\Desktop\\BilibiliVidDownloader\\result'#示例
        programPath = 'C:\\Users\\NTG\\Desktop\\BilibiliVidDownloader'#示例
        VidPath, AduPath = DownVidAdu(VidLink, AduLink, VidName, tempPath, BvId)
        print('下载完成')
        outpath = resultPath + '\\' + VidName + '.mp4'
        ProcessVid(VidPath, AduPath, outpath, programPath)
        print('组装完成')
start()