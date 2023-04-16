import requests
import re
import subprocess
import os
import folder_paths

cwd = os.getcwd ()
# TEXT = '((masterpiece:1.4, best quality)),((masterpiece, best quality)),cute little girl,loli,feel happy,graduate,Cherry blossom on both sides of the road'
LINEFEED = '\n\n'

def init():
    folder_path = cwd+"\\python_embeded\\Lib\\site-packages\\translate"
    tweak_path = cwd +'\\ComfyUI\\web\\extensions\\tweak_keywords_CN2EN'
    tweak_path_bk = cwd + '\\ComfyUI\\custom_nodes\\comfy_translation_node\\tweak_keywords_CN2EN'
    if not os.path.isdir(folder_path):
        print("----------start-------------未发现translate翻译包，正在下载。。。")
        subprocess.run(["pip", "install", "--target="+cwd+"\\python_embeded\\Lib\\site-packages", "translate"])
        print("-----------end------------translate下载完成---如看到黄色提示话术，说明有些依赖是已经安装过了，只要不是error均无需在意")

    if not os.path.isdir(tweak_path):
        print("----------start-------------未发现tweak_keywords_CN2EN文件夹，正在处理。。。")
        os.rename(tweak_path_bk, cwd +'\\ComfyUI\\web\\extensions\\tweak_keywords_CN2EN')
        print("-----------end------------tweak_keywords_CN2EN文件夹处理完成--------------")


    try:
        txtPath = './ComfyUI/custom_nodes/comfy_translation_node/openIE.txt'
        main_path = cwd+'\\ComfyUI\\main.py'
        if os.path.exists(txtPath): 
            f = open(txtPath, "r", encoding="utf-8")
            linesList = f.readlines()
            f.close()
            IEPath = ''
            IEPathOld = ''
            SAVE = ''
            for t in linesList:
                if "PATH=" in t:
                    IEPath = t.replace('PATH=','')
                if "SAVE=" in t:
                    SAVE = t.replace('SAVE=','')
                if "PATHOLD=" in t:
                    IEPathOld = t.replace('PATHOLD=','')
            
            if len(IEPath) < 4 or IEPath == '""':
                return
            print('ewrwere',SAVE == '"FALSE"' or (IEPathOld != IEPath and len(IEPathOld) > 4))
            if SAVE == '"FALSE"' or (IEPathOld != IEPath and len(IEPathOld) > 4):
                from shutil import copyfile
                import fileinput

                if IEPathOld != IEPath and len(IEPathOld) > 4:
                    old = IEPathOld
                    # 定义源文件和备份文件的名字
                    source = main_path
                    # 定义要替换的代码
                    old_code = IEPathOld
                    new_code = """
                                IEPath = """+IEPath+""""""
                    print(old_code,new_code)
                    # 遍历main.py的每一行
                    for line in fileinput.input(main_path, inplace=True): # inplace=True表示修改原文件
                        if line.strip().startswith('IEPath'): # 如果找到要修改的代码
                            line = new_code # 替换成新的代码
                        print(line, end='') # 输出到文件中
                else:
                    old = ''
                    # 定义源文件和备份文件的名字
                    source = main_path
                    backup = cwd+'\\ComfyUI\\main_bk.py'
                    # 复制源文件的内容到备份文件中
                    copyfile(source, backup)
                    
                    # 定义要删除的代码的开头
                    prefix = "webbrowser.open"
                    # 定义要替换的代码
                    old_code = 'import webbrowser'
                    new_code = """
                                import webbrowser

                                IEPath = """+IEPath+"""

                                webbrowser.register('IE', None, webbrowser.BackgroundBrowser(IEPath))

                                webbrowser.get('IE').open("http://{}:{}".format(address, port), new=1,autoraise=True)
"""
                    # 遍历main.py的每一行
                    for line in fileinput.input(main_path, inplace=True): # inplace=True表示修改原文件
                        if line.strip().startswith(prefix): # 如果发现一行以webbrowser.open开头
                            continue # 跳过这一行，不输出到文件中
                        if line.strip() == old_code: # 如果找到要修改的代码
                            line = new_code # 替换成新的代码
                        print(line, end='') # 输出到文件中
                        
                for line in fileinput.input(txtPath, inplace=True): # inplace=True表示修改原文件
                    if line.strip() == 'SAVE="FALSE"': # 如果找到要修改的代码
                        line = line.replace('FALSE', 'TRUE') # 替换成新的代码
                    if line.strip().startswith('PATHOLD'): # 如果找到要修改的代码
                        line = 'PATHOLD='+IEPath+'' # 替换成新的代码
                    print(line, end='') # 输出到文件中
    except :
        pass

def symbol_fun(str):
    # 处理中文符号
    symbol = {ord(f):ord(t) for f,t in zip(
        u'｛｝：，。！？【】（）％＃＠＆１２３４５６７８９０',
        u'{}:，.!?[]()%#@&1234567890')}
    str = str.translate(symbol)
    return str
     
def gg_trans(trans_str,args):
    trans_str = trans_str.replace(';', '#')
    if args['language'] == 'EN':
        from_lang = 'ZH-CN'
        to_lang = 'EN'
    else:
        from_lang = 'EN'
        to_lang = 'ZH-CN'
    # 导入Translator类
    from translate import Translator
    try:
        # 创建一个Translator对象，指定源语言和目标语言
        translator = Translator(from_lang=from_lang, to_lang=to_lang)
        # 调用translate方法来翻译文本
        translation = (translator.translate(trans_str)).replace('#', ';')
        if args['log'] == 'OPEN':
            print('\n调用谷歌请注意查看控制台信息！！！因为谷歌api不稳定，经常调用失败，如果控制台出现500 CHARS时请更换有道api。。。',translator,)
        return translation
    except Exception as e:
        # 打印异常信息
        print("Error:", e)
        return trans_str
    finally:
        # 释放资源
        translator = None

def yd_trans(trans_str,args):
    # 定义有道翻译的网页版地址
    YOUDAO_URL = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'

    if args['language'] == 'EN':
        from_lang = 'ZH-CN'
        to_lang = 'EN'
    else:
        from_lang = 'EN'
        to_lang = 'ZH-CN'
        
    # 构造请求参数
    data = {
        'i': trans_str,
        'from': from_lang,
        'to': to_lang,
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME',
        'typoResult': 'false'
    }

    try:
        # 发送请求并获取响应
        response = requests.post(YOUDAO_URL, data=data)
        if response.status_code == 200:
            result = response.json()
            # 打印翻译结果
            result_text = ''
            tgt_list = result['translateResult'][0]
            # 循环获取tgt
            # loop gain TGT
            for i in tgt_list:
                result_text = result_text+i['tgt']
            return result_text
        else:
            if args['log'] == 'OPEN':
                print(LINEFEED+"调用翻译失败，未进行翻译，原数据返回（call translation failure, not for translation, the original data back）>>>>>>：",trans_str,LINEFEED)
            return trans_str
    except Exception as e:
        # 打印异常信息
        print("Error:", e)
        return trans_str
    finally:
        # 释放资源
        response = None

def trans(args):
    text = args['text']
    if not args or not text:
        return ''
    if args['language'] == 'AUTO':
        return text
    text = 'start' + symbol_fun(text) + 'end'

    if args['language'] == 'EN':
        # 匹配非中文字符的范围
        no_chinese_re = re.compile(r'[\u4e00-\u9fff]+')
        # 使用replace或sub方法，将匹配到的非中文字符替换为,
        no_chinese_re = no_chinese_re.sub('/', text)

        # 匹配中文字符的范围
        chinese_re = re.compile(r'[^\u4e00-\u9fff]+')
        # 使用replace或sub方法，将匹配到的中文字符替换为,
        chinese_re = chinese_re.sub(',', text)

        chinese_re_arr = chinese_re.split(",")
        no_chinese_re_arr = no_chinese_re.split("/")
        del chinese_re_arr[0]
        del chinese_re_arr[-1]
        text_data = no_chinese_re_arr
        trans_str = ';'.join(chinese_re_arr)
        # 调用翻译
        if args['transAPI'] == 'GOOGLE':
            result_text = gg_trans(trans_str,args)
        elif args['transAPI'] == 'YOUDAO':
            result_text = yd_trans(trans_str,args)
        
        # 用逗号作为分隔符，拆分字符串到数组里
        result_text_arr = result_text.split(";")

        text_new = ''
        for i,item in enumerate(text_data):
                if (i<len(result_text_arr)):
                    text_new = text_new + item + result_text_arr[i].strip()
                else:
                    text_new = text_new + item
        text_new = re.sub(r"^(start)|(end)$", "", text_new.replace('，',','))
        if args['log'] == 'OPEN':
            print(LINEFEED,'调用'+args['transAPI']+'转换后的内容如下（The converted contents are as follows）↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓',LINEFEED,text_new,LINEFEED,'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑',LINEFEED)
        return text_new
    elif args['language'] == 'CN':
        text = re.sub(r"^(start)|(end)$", "", text.replace('，',','))
        # 调用翻译
        if args['transAPI'] == 'GOOGLE':
            result_text = gg_trans(text,args)
        elif args['transAPI'] == 'YOUDAO':
            result_text = yd_trans(text,args)
        if args['log'] == 'OPEN':
            print(LINEFEED,'调用'+args['transAPI']+'转换后的内容如下（The converted contents are as follows）↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓',LINEFEED,result_text,LINEFEED,'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑',LINEFEED)
        return result_text
    
    

# trans({"text": TEXT, "language": 'EN', "log": "OPEN", "transAPI":"YOUDAO"})

inputTypes = {
        "required": {
            "text": ("STRING",
                {
                    "multiline": True
                }),
            # "clip": ("CLIP", ),
            "language": (['AUTO','CN','EN'], ),
            "transAPI": (['YOUDAO','GOOGLE'], ),
            "log": (['CLOSE','OPEN'], ),
        }
    }
try:
    embeddingsFile = folder_paths.get_filename_list("embeddings")
    embeddingsList = ['none']
    embeddingsList = embeddingsList + embeddingsFile
    emb = {
        "embeddings": (embeddingsList, ),
        "embeddingsStrength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
    }
    inputTypes['required'].update(emb)
except:
    emb = {}

class CN2ENTRANS:
    @classmethod
    def INPUT_TYPES(s):
        return inputTypes
    RETURN_TYPES = ("STRING",)
    FUNCTION = "text_trans"
    OUTPUT_NODE = True
    CATEGORY = "utils"

    if len(emb) > 0:
        def text_trans(self, text,language,log,transAPI,embeddings,embeddingsStrength):
            print('embeddingsStrength============',embeddingsStrength)
            text = trans({"text": text, "language": language, "log": log, "transAPI": transAPI})
            if  embeddings == 'none':
                if log == 'OPEN':
                    print('no embeddings----------',text)
                return (text,)
            textEmb = '{} embeddings: {} : {},'
            textEmb = textEmb.format(text, embeddings, format(embeddingsStrength,'.3f'))
            if log == 'OPEN':
                print('add embeddings----------',textEmb)
            return (textEmb,)
    else:
        def text_trans(self, text,language,log,transAPI):
            text = trans({"text": text, "language": language, "log": log, "transAPI": transAPI})
            if log == 'OPEN':
                print('no embeddings----------',text)
            return (text,)


class TWEAKKEYWORDS:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"forceInput": True}),
        }}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "tweak_keywords"
    OUTPUT_NODE = True

    CATEGORY = "utils"

    def tweak_keywords(self, text):   
        return {"ui": { "text": text }, "result": (text,)}

NODE_CLASS_MAPPINGS = {
    "CLIP Text Encode CN2EN": CN2ENTRANS,
    "Tweak Keywords CN2EN": TWEAKKEYWORDS,
}
init()